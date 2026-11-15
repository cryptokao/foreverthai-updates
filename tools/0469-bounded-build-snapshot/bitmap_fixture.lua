
 created={}; UIParent={}; STANDARD_TEXT_FONT='fixture-english-only'
 local methods={}
 function methods:SetPoint(...) self.point={...} end
 function methods:SetSize(w,h) self.width=w;self.height=h end
 function methods:SetWidth(w) self.width=w end
 function methods:SetHeight(h) self.height=h end
 function methods:Show() self.visible=true end
 function methods:Hide() self.visible=false end
 function methods:SetTexture(v) self.texture=v end
 function methods:SetTexCoord(...) self.uv={...} end
 function methods:SetText(v) self.text=v end
 function methods:GetStringWidth() return #(self.text or '')*8 end
 function methods:ClearAllPoints() self.point=nil end
 function methods:SetFont(...) end
 function methods:SetTextColor(...) end
 function methods:SetVertexColor(...) end
 local function object(kind) local o=setmetatable({kind=kind,visible=false},{__index=methods}); created[#created+1]=o; return o end
 function methods:CreateTexture(...) return object('texture') end
 function methods:CreateFontString(...) return object('label') end
 function CreateFrame(...) return object('frame') end
 