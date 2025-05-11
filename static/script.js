$(document).ready(function() {
    const $mainImage = $("#lesson-image");
    const defaultSrc = $mainImage.attr("src");

    $(".audio-control").each(function() {
        const audio = this;
        const $container = $(audio).closest(".audio-item");
        const playingSrc = $container.data("image-playing");

        $(audio).on("play", function() {
            $(".audio-control").not(this).each(function() {
                this.pause();
            });
            $mainImage.attr("src", playingSrc);
        });

        $(audio).on("pause ended", function() {
            $mainImage.attr("src", defaultSrc);
        });
    });
});
