import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1920; S=3   # draw at 3x, downscale for crisp edges
FONT="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
def gold_text(text, size, cy, depth):
    f=ImageFont.truetype(FONT,size*S); big=Image.new("RGBA",(W*S,H*S),(0,0,0,0)); d=ImageDraw.Draw(big)
    tw=d.textlength(text,font=f); x=(W*S-tw)/2-30*S; y=cy*S
    # shadow
    sh=Image.new("RGBA",big.size,(0,0,0,0)); ImageDraw.Draw(sh).text((x+(depth+4)*S,y+(depth+10)*S),text,font=f,fill=(0,0,0,235))
    big.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9*S)))
    # extrusion: dark bronze
    for i in range(depth*S,0,-1):
        k=0.45+0.35*(1-i/(depth*S))
        d.text((x+i*0.5,y+i),text,font=f,fill=(int(150*k),int(98*k),int(22*k),255),stroke_width=S,stroke_fill=(int(90*k),int(55*k),int(10*k),255))
    # face mask -> vertical metallic gold gradient
    m=Image.new("L",big.size,0); ImageDraw.Draw(m).text((x,y),text,font=f,fill=255,stroke_width=S,stroke_fill=255)
    bb=m.getbbox(); h0,h1=bb[1],bb[3]
    t=np.clip((np.arange(big.size[1])-h0)/max(1,h1-h0),0,1)
    stops=[(0,(255,244,190)),(0.35,(250,206,92)),(0.55,(214,150,30)),(0.75,(245,196,70)),(1,(255,226,140))]
    def col(v):
        for (a,ca),(b,cb) in zip(stops,stops[1:]):
            if v<=b: u=(v-a)/(b-a); return [ca[j]+(cb[j]-ca[j])*u for j in range(3)]
        return stops[-1][1]
    grad=np.array([col(v) for v in t],dtype=np.uint8)[:,None,:].repeat(big.size[0],1)
    face=Image.fromarray(grad,"RGB").convert("RGBA"); face.putalpha(m)
    big.alpha_composite(face)
    # thin dark outline for contrast
    ol=Image.new("RGBA",big.size,(0,0,0,0)); ImageDraw.Draw(ol).text((x,y),text,font=f,fill=(0,0,0,0),stroke_width=2*S,stroke_fill=(60,35,5,255))
    big=Image.alpha_composite(ol,big)
    return big.resize((W,H),Image.LANCZOS)
im=Image.new("RGBA",(W,H),(0,0,0,0))
im.alpha_composite(gold_text("BUY NOW · $29",84,1410,9))
im.alpha_composite(gold_text("LINK IN BIO!",66,1525,7))
im.save("cta_gold.png")
