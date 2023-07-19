let imageIndex = 0;

function updateImage() {
    const image = document.getElementById("image");
    image.src = "imagenes_show/imagen" + imageIndex + ".png";
    console.log("Imagen actualizada a: " + image.src);
}

document.getElementById("next").addEventListener("click", function() {
    imageIndex++;
    updateImage();
    console.log("Botón Siguiente presionado. Índice de imagen ahora en: " + imageIndex);
});

document.getElementById("prev").addEventListener("click", function() {
    if (imageIndex > 0) {
        imageIndex--;
    }
    updateImage();
    console.log("Botón Anterior presionado. Índice de imagen ahora en: " + imageIndex);
});

console.log("JavaScript cargado correctamente");
