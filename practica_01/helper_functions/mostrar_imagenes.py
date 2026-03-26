import matplotlib.pyplot as plt 

def show_images(img, time):
    plt.imshow(img)
    plt.axis("off")
    plt.show(block=False) # cerrar por si sola la imagen
    plt.pause(time)
    plt.close()
