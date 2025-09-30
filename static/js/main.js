const responsive = {
    0: { items: 1 },
    320: { items: 1 },
    560: { items: 2 },
    960: { items: 3 }
};

$(document).ready(function () {

    let $nav = $('.nav');
    let $toggleCollapse = $('.toggle-collapse');

    // Toggle menu
    $toggleCollapse.click(function () {
        $nav.toggleClass('collapse');
    });

    // Owl Carousel for blog
    $('.owl-carousel').owlCarousel({
        loop: true,
        autoplay: false,
        autoplayTimeout: 3000,
        dots: false,
        nav: true,
        navText: ["<i class='fas fa-long-arrow-alt-left'></i>", "<i class='fas fa-long-arrow-alt-right'></i>"],
        responsive: responsive
    });

    // Scroll to top
    $('.move-up span').click(function () {
        $('html, body').animate({ scrollTop: 0 }, 1000);
    });

    // Initialize AOS once
    AOS.init();

    // Number counter animation
    let nCount = function (selector) {
        $(selector).each(function () {
            $(this).animate({ Counter: $(this).text() }, {
                duration: 4000,
                easing: "swing",
                step: function (value) {
                    $(this).text(Math.ceil(value));
                }
            });
        });
    };

    let a = 0;
    if ($(".numbers").length) {
        $(window).scroll(function () {
            let oTop = $(".numbers").offset().top - window.innerHeight;
            if (a === 0 && $(window).scrollTop() >= oTop) {
                a++;
                nCount(".rect > h1");
            }
        });
    }
});
