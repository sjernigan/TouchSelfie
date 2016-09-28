from PIL import Image

# png = Image.open("./mylogo2.png").convert('RGBA').resize((1000, 667))
# #background = Image.new('RGBA', png.size, (255,255,255))
# background = Image.open("./photo.jpg").convert('RGBA')
# alpha_composite = Image.alpha_composite(background, png)
# alpha_composite.save('foo.jpg', 'JPEG', quality=80)

snapshot = Image.open("./samples/photo.jpg")
#snapshot = Image.new('RGBA', (1366, 768))
size = snapshot.size

logo = Image.open("./mylogo2.png").convert('RGBA')
logo_size = logo.size
print "my logo size is ",  logo_size[0], "," , logo_size[1]
print "image size is ",  size[0], "," , size[1]
yoff = (size[1] - logo_size[1]) // 2
xoff = (size[0] - logo_size[0]) // 2
print "offset is ",  xoff, "," , yoff
snapshot.paste(logo,(xoff, yoff), logo)
snapshot.save("./output.png")

# png = Image.open("./mylogo.png")
# png.load() # required for png.split()
# background = Image.new("RGB", png.size, (255, 255, 255))
# background.paste(png, mask=png.split()[3]) # 3 is the alpha channel
# background.save('foo.jpg', 'JPEG', quality=80)


