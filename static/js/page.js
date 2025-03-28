document.addEventListener('DOMContentLoaded', function() {
            // Hero Slider
            const slides = document.querySelectorAll('.hero-slide');
            const dots = document.querySelectorAll('.dot');
            let currentSlide = 0;
            let slideInterval;

            function showSlide(index) {
                slides.forEach(slide => slide.classList.remove('active'));
                dots.forEach(dot => dot.classList.remove('active'));

                slides[index].classList.add('active');
                dots[index].classList.add('active');
                currentSlide = index;
            }

            function nextSlide() {
                let nextIndex = (currentSlide + 1) % slides.length;
                showSlide(nextIndex);
            }

            function startSlider() {
                slideInterval = setInterval(nextSlide, 5000);
            }

            function stopSlider() {
                clearInterval(slideInterval);
            }

            // Initialize slider
            showSlide(0);
            startSlider();

            // Dot navigation
            dots.forEach((dot, index) => {
                dot.addEventListener('click', () => {
                    stopSlider();
                    showSlide(index);
                    startSlider();
                });
            });

            // Next/prev buttons
            document.querySelector('.next-slide').addEventListener('click', () => {
                stopSlider();
                nextSlide();
                startSlider();
            });

            document.querySelector('.prev-slide').addEventListener('click', () => {
                stopSlider();
                let prevIndex = (currentSlide - 1 + slides.length) % slides.length;
                showSlide(prevIndex);
                startSlider();
            });

            // Tab functionality
            const tabButtons = document.querySelectorAll('.tab-btn');
            const tabPanes = document.querySelectorAll('.tab-pane');

            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const tabId = button.getAttribute('data-tab');

                    // Update active tab button
                    tabButtons.forEach(btn => btn.classList.remove('active', 'border-accent', 'bg-white'));
                    button.classList.add('active', 'border-accent', 'bg-white');

                    // Update active tab pane
                    tabPanes.forEach(pane => pane.classList.add('hidden'));
                    document.getElementById(tabId).classList.remove('hidden');
                });
            });

            // Scroll Animations
            gsap.utils.toArray('.section-header').forEach(header => {
                ScrollTrigger.create({
                    trigger: header,
                    start: 'top 80%',
                    onEnter: () => header.classList.add('visible'),
                    onLeaveBack: () => header.classList.remove('visible')
                });
            });

            // Navbar Scroll Effect
            window.addEventListener('scroll', () => {
                const navbar = document.querySelector('.navbar');
                if (window.scrollY > 50) {
                    navbar.classList.add('shadow-lg', 'bg-primary');
                    navbar.classList.remove('bg-primary/90');
                } else {
                    navbar.classList.remove('shadow-lg');
                    navbar.classList.add('bg-primary/90');
                }
            });

            // Smooth scrolling for anchor links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    e.preventDefault();

                    const targetId = this.getAttribute('href');
                    const targetElement = document.querySelector(targetId);

                    if (targetElement) {
                        window.scrollTo({
                            top: targetElement.offsetTop - 80,
                            behavior: 'smooth'
                        });
                    }
                });
            });

            // Modal functionality
            const modal = document.querySelector('.modal');
            const closeModal = document.querySelector('.close-modal');
            const productLinks = document.querySelectorAll('[data-product]');

            closeModal.addEventListener('click', () => {
                modal.classList.add('hidden');
            });

            window.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                }
            });
        });