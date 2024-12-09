function Image(elem)
  if elem.attributes.height then
    elem.attributes.height = ""
    elem.attributes.style = 'margin:auto;height:auto'
  end

  return elem
end

function is_image_followed_by_paragraph(image, para)
  return image and image.content[1].t == 'Image' and para
end

function Blocks (blocks)
  for i = #blocks-1, 1, -1 do
    local first, second = blocks[i], blocks[i + 1]
    if is_image_followed_by_paragraph(blocks[i], blocks[i + 1]) then
      local div = pandoc.Div({
        first,
        second
      }, {style = "text-align:center"})

      blocks:remove(i)
      blocks:remove(i)

      blocks:insert(i, div)
    end

    if first.t == "Para" then
      local m = manage(first)

      if m then
        for name, body in pairs(m) do
          local div = pandoc.Para({ pandoc.RawInline("markdown", name .. " " .. body) })
          blocks:insert(i+1, div)
        end
      end
    end
  end
  return blocks
end

function removeRange(tbl, start, finish)
    for i = finish, start, -1 do
        table.remove(tbl, i)
    end
end

function trim1(s)
   return (s:gsub("^%s*(.-)%s*$", "%1"))
end

function manage(elem)
  local ret = {}

  local footnote_pattern = "%[%^([%w%-_]+)%]:%s*.*"

  local found_note = nil
  local note_str = ""
  local note_name = ""
  local note_begin = 1

  for i, e in ipairs(elem.c) do
    if e.t == "Str" then
      if found_note then
        if e.text:find("\\e") then
          note_str = note_str .. e.text:gsub("\\e", "")
          ret[note_name] = note_str

          if note_begin-1 >= 1 and elem.c[note_begin-1].t == "Space" then
            note_begin = note_begin - 1
          end
          removeRange(elem.c, note_begin, i)

          found_note = nil
        elseif e.text:find("\\n") then
          note_str = note_str .. e.text:gsub("\\n", "<br>")
        else
          note_str = note_str .. e.text
        end
      end

      local footnote_ref, body = string.match(e.text, footnote_pattern)

      if footnote_ref then
        found_note = footnote_ref
        note_str = ""
        note_name = e.text
        e.text, _ = trim1(e.text):gsub(":", "")
        elem.c[i] = pandoc.RawInline("markdown", e.text)
        note_begin = i + 1
        if elem.c[i+1].t == "Space" then
          elem.c:remove(i+1)
        end
      end
    elseif found_note and e.t == "Space" then
      note_str = note_str .. " "
    end
  end

  return ret
end
