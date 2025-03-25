(function () {
    // DOM Elements
    const sidebar = document.getElementById("sidebar");
    const toggleSidebar = document.getElementById("toggle-sidebar");
    const mobileToggle = document.getElementById("mobile-toggle");
    const mobileOverlay = document.getElementById("mobile-overlay");
    const dropdownTriggers = document.querySelectorAll(".dropdown-trigger");

    // State
    let isSidebarCollapsed = false;
    let isMobileSidebarOpen = false;

    // Check if device is mobile
    const isMobile = () => window.innerWidth < 768;

    // Toggle sidebar on desktop
    toggleSidebar.addEventListener("click", () => {
        console.log("clicked");
        if (isMobile()) return;

        isSidebarCollapsed = !isSidebarCollapsed;

        if (isSidebarCollapsed) {
            sidebar.classList.remove("w-64");
            sidebar.classList.add("w-16");

            // Hide text elements
            document.querySelectorAll(".sidebar-text").forEach((el) => {
                el.classList.add("hidden");
            });

            // Hide group labels
            document.querySelectorAll(".sidebar-group-label").forEach((el) => {
                el.classList.add("opacity-0");
            });

            // Hide search
            document.querySelectorAll(".sidebar-search").forEach((el) => {
                el.classList.add("hidden");
            });

            // Hide dropdown content
            document.querySelectorAll(".dropdown-content").forEach((el) => {
                el.classList.add("hidden");
            });

            // Add tooltip behavior for collapsed mode
            document
                .querySelectorAll(".dropdown-trigger")
                .forEach((trigger) => {
                    trigger.setAttribute("title", "Projects");
                });
        } else {
            sidebar.classList.remove("w-16");
            sidebar.classList.add("w-64");

            // Show text elements
            document.querySelectorAll(".sidebar-text").forEach((el) => {
                el.classList.remove("hidden");
            });

            // Show group labels
            document.querySelectorAll(".sidebar-group-label").forEach((el) => {
                el.classList.remove("opacity-0");
            });

            // Show search
            document.querySelectorAll(".sidebar-search").forEach((el) => {
                el.classList.remove("hidden");
            });

            // Show dropdown content if it was open
            document
                .querySelectorAll(".dropdown-content.is-open")
                .forEach((el) => {
                    el.classList.remove("hidden");
                });

            // Remove tooltips
            document
                .querySelectorAll(".dropdown-trigger")
                .forEach((trigger) => {
                    trigger.removeAttribute("title");
                });
        }
    });

    // Toggle dropdown menus
    dropdownTriggers.forEach((trigger) => {
        trigger.addEventListener("click", () => {
            const parent = trigger.closest(".dropdown-container");
            const content = parent.querySelector(".dropdown-content");
            const icon = trigger.querySelector(".dropdown-icon");

            // Toggle dropdown
            if (content.classList.contains("opacity-0")) {
                // Open dropdown
                content.classList.remove("max-h-0", "opacity-0");
                content.classList.add("max-h-48", "opacity-100", "is-open");
                icon.classList.add("rotate-180");

                // If sidebar is collapsed, don't show dropdown
                if (isSidebarCollapsed) {
                    content.classList.add("hidden");
                }
            } else {
                // Close dropdown
                content.classList.remove("max-h-48", "opacity-100", "is-open");
                content.classList.add("max-h-0", "opacity-0");
                icon.classList.remove("rotate-180");
            }
        });
    });

    // Toggle sidebar on mobile
    mobileToggle.addEventListener("click", () => {
        isMobileSidebarOpen = !isMobileSidebarOpen;

        if (isMobileSidebarOpen) {
            sidebar.classList.add("translate-x-0");
            sidebar.classList.remove("-translate-x-full");
            mobileOverlay.classList.remove("hidden");
        } else {
            sidebar.classList.remove("translate-x-0");
            sidebar.classList.add("-translate-x-full");
            mobileOverlay.classList.add("hidden");
        }
    });

    // Close sidebar when clicking overlay
    mobileOverlay.addEventListener("click", () => {
        isMobileSidebarOpen = false;
        sidebar.classList.remove("translate-x-0");
        sidebar.classList.add("-translate-x-full");
        mobileOverlay.classList.add("hidden");
    });

    // Handle resize events
    window.addEventListener("resize", () => {
        if (isMobile()) {
            // Reset desktop styles
            if (isSidebarCollapsed) {
                sidebar.classList.remove("w-16");
                sidebar.classList.add("w-64");

                document.querySelectorAll(".sidebar-text").forEach((el) => {
                    el.classList.remove("hidden");
                });

                document
                    .querySelectorAll(".sidebar-group-label")
                    .forEach((el) => {
                        el.classList.remove("opacity-0");
                    });

                document.querySelectorAll(".sidebar-search").forEach((el) => {
                    el.classList.remove("hidden");
                });

                // Show dropdown content if it was open
                document
                    .querySelectorAll(".dropdown-content.is-open")
                    .forEach((el) => {
                        el.classList.remove("hidden");
                    });

                isSidebarCollapsed = false;
            }

            // Apply mobile styles
            if (!isMobileSidebarOpen) {
                sidebar.classList.add("-translate-x-full");
                sidebar.classList.remove("translate-x-0");
            }
        } else {
            // Reset mobile styles
            sidebar.classList.remove("-translate-x-full");
            sidebar.classList.add("translate-x-0");
            mobileOverlay.classList.add("hidden");
            isMobileSidebarOpen = false;
        }
    });

    // Initialize mobile view
    if (isMobile()) {
        sidebar.classList.add("-translate-x-full");
    }
})();
