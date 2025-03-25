(function () {
    const sidebar = document.querySelector("#sidebar");
    const toggleSidebar = document.querySelector("#toggle-sidebar");
    const dropdownTriggers = document.querySelectorAll(".dropdown-trigger");
    const toggleSidebarText = document.querySelector("#toggle-sidebar-text");

    // State
    let isSidebarCollapsed = false;
    let isMobileSidebarOpen = false;

    const sidebarMax = "w-[17rem]";
    const sidebarMin = "w-[4rem]";

    // Check if device is mobile
    const isMobile = () => window.innerWidth < 768;

    // Initialize mobile view
    if (isMobile()) {
        toggleSidebarText.innerText = "Open";
        sidebar.classList.add("hidden");
    }

    toggleSidebar.addEventListener("click", () => {
        // console.log("clicked");

        if (isMobile()) {
            isMobileSidebarOpen = !isMobileSidebarOpen;

            if (isMobileSidebarOpen) {
                toggleSidebar.classList.add(
                    "absolute",
                    "z-[200]",
                    "right-0",
                    "top-0",
                );
                sidebar.classList.add("absolute", "z-[100]", "w-[65%]");
                sidebar.classList.remove("hidden");
                toggleSidebarText.innerText = "Close";
            } else {
                toggleSidebar.classList.remove(
                    "absolute",
                    "z-[200]",
                    "right-0",
                    "top-0",
                );
                sidebar.classList.remove("absolute", "z-[100]", "w-[65%]");
                sidebar.classList.add("hidden");
                toggleSidebarText.innerText = "Open";
            }
        } else {
            isSidebarCollapsed = !isSidebarCollapsed;

            if (isSidebarCollapsed) {
                sidebar.classList.remove(sidebarMax);
                sidebar.classList.add(sidebarMin);
                toggleSidebarText.innerText = "Open";

                // Hide text elements
                document.querySelectorAll(".sidebar-text").forEach((el) => {
                    el.classList.add("hidden");
                });

                // Hide dropdown content
                document.querySelectorAll(".dropdown-content").forEach((el) => {
                    el.classList.add("hidden");
                });

                // Add tooltip behavior for collapsed mode
                // document
                //     .querySelectorAll(".dropdown-trigger")
                //     .forEach((trigger) => {
                //         trigger.setAttribute("title", "Projects");
                //     });
            } else {
                sidebar.classList.remove(sidebarMin);
                sidebar.classList.add(sidebarMax);
                toggleSidebarText.innerText = "Close";

                // Show text elements
                document.querySelectorAll(".sidebar-text").forEach((el) => {
                    el.classList.remove("hidden");
                });

                // Show dropdown content if it was open
                document
                    .querySelectorAll(".dropdown-content.is-open")
                    .forEach((el) => {
                        el.classList.remove("hidden");
                    });

                // Remove tooltips
                // document
                //     .querySelectorAll(".dropdown-trigger")
                //     .forEach((trigger) => {
                //         trigger.removeAttribute("title");
                //     });
            }
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
                } else {
                    content.classList.remove("hidden");
                }
            } else {
                // Close dropdown
                content.classList.remove("max-h-48", "opacity-100", "is-open");
                content.classList.add("max-h-0", "opacity-0");
                icon.classList.remove("rotate-180");
            }
        });
    });

    // Handle resize events
    window.addEventListener("resize", () => {
        if (isMobile()) {
            if (isMobileSidebarOpen) {
                toggleSidebar.classList.add(
                    "absolute",
                    "z-[200]",
                    "right-0",
                    "top-0",
                );
                toggleSidebarText.innerText = "Close";
            } else {
                toggleSidebar.classList.remove(
                    "absolute",
                    "z-[200]",
                    "right-0",
                    "top-0",
                );
                toggleSidebarText.innerText = "Open";
            }
            // Reset desktop styles
            if (isSidebarCollapsed) {
                sidebar.classList.remove("absolute", "z-[100]", "w-[65%]");
                sidebar.classList.add(sidebarMax);

                document.querySelectorAll(".sidebar-text").forEach((el) => {
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
                sidebar.classList.add("hidden");
                sidebar.classList.remove("absolute", "z-[100]", "w-[65%]");
            }
        } else {
            if (isSidebarCollapsed) {
                toggleSidebarText.innerText = "Open";
            } else {
                toggleSidebarText.innerText = "Close";
            }

            toggleSidebar.classList.remove(
                "absolute",
                "z-[200]",
                "right-0",
                "top-0",
            );

            // Reset mobile styles
            sidebar.classList.remove(
                "hidden",
                "absolute",
                "z-[100]",
                "w-[65%]",
            );
            sidebar.classList.add(sidebarMax);
            isMobileSidebarOpen = false;
        }
    });
})();
