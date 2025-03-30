export function setActiveLink() {
    const path = window.location.pathname.slice(1);
    // console.log(path);

    document.querySelectorAll(".link").forEach((element) => {
        // console.log(element.id);

        if (element.id === path) {
            element.classList.add("bg-[#0065FA]/70", "rounded-lg");
        } else {
            element.classList.remove("bg-[#0065FA]/70", "rounded-lg");
        }
    });

    // Highlight dropdowns button for active links
    document.querySelectorAll(".d-btn").forEach((element) => {
        if (element.classList.contains(`d-btn-${path}`)) {
            element.classList.add("bg-[#0065FA]/70", "rounded-lg");
        } else {
            element.classList.remove("bg-[#0065FA]/50", "rounded-lg");
        }
    });
}

export function handleSidebar() {
    try {
        const sidebar = document.querySelector("#sidebar");
        const toggleSidebarBtn = document.querySelector("#toggle-sidebar-btn");
        const dropdownTriggers = document.querySelectorAll(".dropdown-trigger");
        const toggleSidebarText = document.querySelector(
            "#toggle-sidebar-text",
        );
        const authLayoutDiv = document.querySelector("#authlayout-div");

        // State
        let isSidebarCollapsed = false;
        let isMobileSidebarOpen = false;

        const sidebarMax = "w-[15rem]";
        const sidebarMin = "w-[4rem]";

        const sidebarBtnLeft = "left-[15rem]";

        const authLayoutDivMax = "md:ml-[16rem]";
        const authLayoutDivMin = "ml-[5rem]";

        // Check if device is mobile
        const isMobile = () => window.innerWidth < 768;

        // Initialize mobile view
        if (isMobile()) {
            toggleSidebarText.innerText = "Open";
            sidebar.classList.add("hidden");
        }

        toggleSidebarBtn.addEventListener("click", () => {
            // console.log("clicked");

            if (isMobile()) {
                isMobileSidebarOpen = !isMobileSidebarOpen;

                if (isMobileSidebarOpen) {
                    toggleSidebarBtn.classList.add(sidebarBtnLeft, "top-0");
                    toggleSidebarText.innerText = "Close";

                    sidebar.classList.add(sidebarMax);
                    sidebar.classList.remove("hidden");
                } else {
                    toggleSidebarBtn.classList.remove(sidebarBtnLeft, "top-0");
                    toggleSidebarText.innerText = "Open";

                    sidebar.classList.remove(sidebarMax);
                    sidebar.classList.add("hidden");
                }
            } else {
                isSidebarCollapsed = !isSidebarCollapsed;

                if (isSidebarCollapsed) {
                    sidebar.classList.remove(sidebarMax);
                    sidebar.classList.add(sidebarMin);

                    authLayoutDiv.classList.remove(authLayoutDivMax);
                    authLayoutDiv.classList.add(authLayoutDivMin);

                    toggleSidebarText.innerText = "Open";

                    // Hide text elements
                    document.querySelectorAll(".sidebar-text").forEach((el) => {
                        el.classList.add("hidden");
                    });

                    // Hide dropdown content
                    document
                        .querySelectorAll(".dropdown-content")
                        .forEach((el) => {
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

                    authLayoutDiv.classList.add(authLayoutDivMax);
                    authLayoutDiv.classList.remove(authLayoutDivMin);

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

        // Handle resize events
        window.addEventListener("resize", () => {
            if (isMobile()) {
                if (isMobileSidebarOpen) {
                    toggleSidebarBtn.classList.add(sidebarBtnLeft, "top-0");
                    toggleSidebarText.innerText = "Close";
                } else {
                    toggleSidebarBtn.classList.remove(sidebarBtnLeft, "top-0");
                    toggleSidebarText.innerText = "Open";
                }
                // Reset desktop styles
                if (isSidebarCollapsed) {
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
                    sidebar.classList.remove(sidebarMax);
                }
            } else {
                if (isSidebarCollapsed) {
                    authLayoutDiv.classList.remove(authLayoutDivMax);
                    authLayoutDiv.classList.add(authLayoutDivMin);

                    toggleSidebarText.innerText = "Open";
                } else {
                    authLayoutDiv.classList.add(authLayoutDivMax);
                    authLayoutDiv.classList.remove(authLayoutDivMin);

                    toggleSidebarText.innerText = "Close";
                }

                toggleSidebarBtn.classList.remove(sidebarBtnLeft, "top-0");

                // Reset mobile styles
                sidebar.classList.remove("hidden");
                sidebar.classList.add(sidebarMax);
                isMobileSidebarOpen = false;
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
                    content.classList.remove(
                        "max-h-48",
                        "opacity-100",
                        "is-open",
                    );
                    content.classList.add("max-h-0", "opacity-0");
                    icon.classList.remove("rotate-180");
                }
            });
        });
    } catch (error) {}
}
