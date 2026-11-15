window.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('system-loader');
    const pageShell = document.getElementById('page-shell');
    const loaderShownAt = performance.now();
    const hideLoader = () => {
        if (!loader) return;
        loader.style.opacity = '0';
        loader.style.visibility = 'hidden';
    };
    const showLoader = () => {
        if (!loader) return;
        loader.style.visibility = 'visible';
        loader.style.opacity = '1';
    };
    if (pageShell) window.requestAnimationFrame(() => pageShell.classList.add('is-ready'));
    if (loader) {
        const minimumDisplayMs = 550;
        const elapsedMs = performance.now() - loaderShownAt;
        const remainingMs = Math.max(0, minimumDisplayMs - elapsedMs);
        window.setTimeout(hideLoader, remainingMs);
    }

    document.addEventListener('click', (event) => {
        const link = event.target.closest('a[href]');
        if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || link.target === '_blank' || link.hasAttribute('download')) return;
        const destination = new URL(link.href, window.location.href);
        if (destination.origin !== window.location.origin) return;
        if (destination.pathname === window.location.pathname && destination.search === window.location.search && destination.hash) return;
        showLoader();
    });
    window.addEventListener('pagehide', showLoader);
    window.addEventListener('pageshow', (event) => {
        if (event.persisted) hideLoader();
    });

    const stickyNavigation = document.querySelector('navbar');
    if (stickyNavigation) {
        let scrollFrame = 0;
        window.addEventListener('scroll', () => {
            if (scrollFrame) return;
            scrollFrame = window.requestAnimationFrame(() => {
                stickyNavigation.classList.toggle('is-scrolled', window.scrollY > 18);
                scrollFrame = 0;
            });
        }, { passive: true });
        stickyNavigation.classList.toggle('is-scrolled', window.scrollY > 18);
    }

    const menuButton = document.querySelector('.menu-toggle');
    const navigation = document.getElementById('primary-navigation');
    if (!menuButton || !navigation) return;

    const setMenuOpen = (isOpen) => {
        menuButton.setAttribute('aria-expanded', String(isOpen));
        menuButton.setAttribute('aria-label', isOpen ? 'Close navigation menu' : 'Open navigation menu');
        const menuLabel = menuButton.querySelector('.menu-toggle-label');
        if (menuLabel) menuLabel.textContent = isOpen ? 'Close' : 'Menu';
        navigation.classList.toggle('is-open', isOpen);
    };

    menuButton.addEventListener('click', () => {
        setMenuOpen(menuButton.getAttribute('aria-expanded') !== 'true');
    });
    navigation.addEventListener('click', (event) => {
        if (event.target.closest('a')) setMenuOpen(false);
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
            setMenuOpen(false);
            menuButton.focus();
        }
    });
    const closeMenuOnDesktop = () => {
        if (window.innerWidth > 760) setMenuOpen(false);
    };
    window.addEventListener('resize', closeMenuOnDesktop);

    const accessibilityTrigger = document.querySelector('.accessibility-trigger');
    const accessibilityPanel = document.getElementById('accessibility-panel');
    const accessibilityClose = document.querySelector('[data-accessibility-close]');
    const accessibilityStatus = document.getElementById('accessibility-status');
    const accessButtons = document.querySelectorAll('[data-access-setting]');
    const accessStorageKey = 'coreNodeAccessibility';
    let accessPreferences = { darkMode: true, highContrast: false, textScale: 'normal', fontStyle: 'theme', reduceMotion: false };
    let voiceAssistantEnabled = false;
    try {
        const savedPreferences = JSON.parse(window.localStorage.getItem(accessStorageKey) || 'null');
        if (savedPreferences) accessPreferences = { ...accessPreferences, ...savedPreferences };
    } catch (error) {
        // Accessibility controls remain available when browser storage is disabled.
    }

    const applyAccessPreferences = () => {
        document.documentElement.classList.toggle('accessibility-large-text', accessPreferences.textScale === 'large');
        document.documentElement.classList.toggle('accessibility-small-text', accessPreferences.textScale === 'small');
        ['inter', 'opensans', 'lexend', 'georgia'].forEach((font) => {
            document.documentElement.classList.toggle(`accessibility-font-${font}`, accessPreferences.fontStyle === font);
        });
        document.body.classList.toggle('accessibility-light-mode', !accessPreferences.darkMode);
        document.body.classList.toggle('accessibility-high-contrast', accessPreferences.highContrast);
        document.body.classList.toggle('accessibility-reduce-motion', accessPreferences.reduceMotion);
        accessButtons.forEach((button) => {
            const setting = button.dataset.accessSetting;
            let isPressed = false;
            if (setting === 'dark-mode') isPressed = accessPreferences.darkMode;
            if (setting === 'high-contrast') isPressed = accessPreferences.highContrast;
            if (setting === 'larger-text') isPressed = accessPreferences.textScale === 'large';
            if (setting === 'smaller-text') isPressed = accessPreferences.textScale === 'small';
            if (setting === 'default-text') isPressed = accessPreferences.textScale === 'normal';
            if (setting.startsWith('font-')) isPressed = accessPreferences.fontStyle === setting.slice(5);
            if (setting === 'voice-assistant') isPressed = voiceAssistantEnabled;
            if (setting === 'reduce-motion') isPressed = accessPreferences.reduceMotion;
            if (setting !== 'reset') button.setAttribute('aria-pressed', String(isPressed));
        });
    };
    const saveAccessPreferences = (announcement) => {
        applyAccessPreferences();
        const savedPreferences = { ...accessPreferences };
        delete savedPreferences.voiceAssistant;
        try { window.localStorage.setItem(accessStorageKey, JSON.stringify(savedPreferences)); } catch (error) { /* Keep the setting for this page view. */ }
        if (accessibilityStatus) accessibilityStatus.textContent = announcement;
    };

    if (accessibilityTrigger && accessibilityPanel) {
        const setAccessibilityPanelOpen = (isOpen) => {
            accessibilityTrigger.setAttribute('aria-expanded', String(isOpen));
            accessibilityTrigger.setAttribute('aria-label', isOpen ? 'Close accessibility options' : 'Open accessibility options');
            accessibilityPanel.setAttribute('aria-hidden', String(!isOpen));
            accessibilityPanel.inert = !isOpen;
            accessibilityPanel.classList.toggle('is-open', isOpen);
            document.body.classList.toggle('accessibility-drawer-open', isOpen);
            if (isOpen) accessibilityClose?.focus();
        };
        accessibilityTrigger.addEventListener('click', () => {
            setAccessibilityPanelOpen(accessibilityTrigger.getAttribute('aria-expanded') !== 'true');
        });
        accessibilityClose?.addEventListener('click', () => {
            setAccessibilityPanelOpen(false);
            accessibilityTrigger.focus();
        });
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && accessibilityTrigger.getAttribute('aria-expanded') === 'true') {
                setAccessibilityPanelOpen(false);
                accessibilityTrigger.focus();
            }
        });
        accessButtons.forEach((button) => {
            button.addEventListener('click', () => {
                const setting = button.dataset.accessSetting;
                if (setting === 'dark-mode') accessPreferences.darkMode = !accessPreferences.darkMode;
                if (setting === 'high-contrast') accessPreferences.highContrast = !accessPreferences.highContrast;
                if (setting === 'larger-text') accessPreferences.textScale = 'large';
                if (setting === 'smaller-text') accessPreferences.textScale = 'small';
                if (setting === 'default-text') accessPreferences.textScale = 'normal';
                if (setting.startsWith('font-')) accessPreferences.fontStyle = setting.slice(5);
                if (setting === 'reduce-motion') accessPreferences.reduceMotion = !accessPreferences.reduceMotion;
                if (setting === 'voice-assistant') {
                    if (!('speechSynthesis' in window)) {
                        if (accessibilityStatus) accessibilityStatus.textContent = 'Voice assistant is not supported by this browser.';
                        return;
                    }
                    voiceAssistantEnabled = !voiceAssistantEnabled;
                    if (!voiceAssistantEnabled) window.speechSynthesis.cancel();
                }
                if (setting === 'reset') {
                    accessPreferences = { darkMode: true, highContrast: false, textScale: 'normal', fontStyle: 'theme', reduceMotion: false };
                    voiceAssistantEnabled = false;
                    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
                }
                const announcements = {
                    'dark-mode': `Dark mode ${accessPreferences.darkMode ? 'enabled' : 'disabled'}.`,
                    'high-contrast': `High contrast ${accessPreferences.highContrast ? 'enabled' : 'disabled'}.`,
                    'larger-text': 'Text size increased.',
                    'smaller-text': 'Text size decreased.',
                    'default-text': 'Default text size restored.',
                    'font-inter': 'Inter font selected.',
                    'font-opensans': 'Open Sans font selected.',
                    'font-lexend': 'Lexend font selected.',
                    'font-georgia': 'Georgia font selected.',
                    'font-theme': 'CORE_NODE default font selected.',
                    'voice-assistant': `Voice assistant ${voiceAssistantEnabled ? 'enabled. Select text to hear it read aloud' : 'disabled'}.`,
                    'reduce-motion': `Reduced motion ${accessPreferences.reduceMotion ? 'enabled' : 'disabled'}.`,
                    reset: 'Display settings reset.'
                };
                saveAccessPreferences(announcements[setting]);
            });
        });
        let lastSpokenSelection = '';
        document.addEventListener('selectionchange', () => {
            const selectedText = window.getSelection()?.toString().trim();
            if (!voiceAssistantEnabled || !selectedText || selectedText === lastSpokenSelection) return;
            lastSpokenSelection = selectedText;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(new SpeechSynthesisUtterance(selectedText));
        });
        applyAccessPreferences();
    }

    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            const status = document.getElementById('contact-form-status');
            const submitButton = contactForm.querySelector('button[type="submit"]');
            if (contactForm.dataset.authenticated !== 'true') {
                if (status) status.textContent = 'Signing in is required. Redirecting to sign in…';
                if (window.showCyberAlert) {
                    window.showCyberAlert('AUTHENTICATION REQUIRED: Sign in with a registered account before sending an email.', 'error', contactForm);
                }
                return;
            }
            if (submitButton && window.setButtonProcessing) {
                window.setButtonProcessing(submitButton, 'Transmitting Signal...');
            }
            const name = contactForm.elements.name.value.trim();
            const email = contactForm.elements.email.value.trim();
            const message = contactForm.elements.message.value.trim();
            const subject = `Portfolio contact from ${name}`;
            const body = `${message}\n\nFrom: ${name}\nReply to: ${email}`;
            const mailto = `mailto:osanodavid09@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
            window.open(mailto, '_blank');
            if (status) status.textContent = 'Email draft opened. Review it and press Send in your email app.';
        });
    }

    const accordionRuns = new WeakMap();
    const accordionCleanups = new WeakMap();
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const animateAccordion = (details, shouldOpen) => {
        const previousCleanup = accordionCleanups.get(details);
        if (previousCleanup) previousCleanup();
        const content = details.querySelector(':scope > .project-content');
        if (!content) {
            details.open = shouldOpen;
            return;
        }

        const runId = (accordionRuns.get(details) || 0) + 1;
        accordionRuns.set(details, runId);

        if (shouldOpen) {
            details.open = true;
            content.classList.remove('is-expanded');
            content.style.height = '0px';
            content.style.opacity = '0';
            content.style.transform = 'translateY(-0.5rem)';
            content.offsetHeight;
            requestAnimationFrame(() => {
                if (accordionRuns.get(details) !== runId) return;
                content.style.height = `${content.scrollHeight}px`;
                content.style.opacity = '1';
                content.style.transform = 'translateY(0)';
            });

            let timer;
            const cleanup = () => {
                content.removeEventListener('transitionend', finishOpening);
                window.clearTimeout(timer);
                if (accordionCleanups.get(details) === cleanup) accordionCleanups.delete(details);
            };
            const finishOpening = (event) => {
                if (event && (event.target !== content || event.propertyName !== 'height')) return;
                if (accordionRuns.get(details) !== runId) {
                    cleanup();
                    return;
                }
                content.classList.add('is-expanded');
                content.style.removeProperty('height');
                content.style.removeProperty('opacity');
                content.style.removeProperty('transform');
                cleanup();
            };
            accordionCleanups.set(details, cleanup);
            content.addEventListener('transitionend', finishOpening);
            timer = window.setTimeout(() => finishOpening(), reducedMotion ? 20 : 480);
            return;
        }

        if (!details.open) return;
        const currentHeight = content.getBoundingClientRect().height;
        content.classList.remove('is-expanded');
        content.style.height = `${currentHeight}px`;
        content.style.opacity = '1';
        content.style.transform = 'translateY(0)';
        content.offsetHeight;
        requestAnimationFrame(() => {
            if (accordionRuns.get(details) !== runId) return;
            content.style.height = '0px';
            content.style.opacity = '0';
            content.style.transform = 'translateY(-0.5rem)';
        });

        let timer;
        const cleanup = () => {
            content.removeEventListener('transitionend', finishClosing);
            window.clearTimeout(timer);
            if (accordionCleanups.get(details) === cleanup) accordionCleanups.delete(details);
        };
        const finishClosing = (event) => {
            if (event && (event.target !== content || event.propertyName !== 'height')) return;
            if (accordionRuns.get(details) !== runId) {
                cleanup();
                return;
            }
            details.open = false;
            content.style.removeProperty('height');
            content.style.removeProperty('opacity');
            content.style.removeProperty('transform');
            cleanup();
        };
        accordionCleanups.set(details, cleanup);
        content.addEventListener('transitionend', finishClosing);
        timer = window.setTimeout(() => finishClosing(), reducedMotion ? 20 : 480);
    };

    document.querySelectorAll('[data-project-accordion]').forEach((details) => {
        const summary = details.querySelector(':scope > summary');
        if (!summary) return;
        summary.addEventListener('click', (event) => {
            event.preventDefault();
            const grid = details.closest('.project-grid');
            if (details.open) {
                animateAccordion(details, false);
                return;
            }
            if (grid) {
                grid.querySelectorAll('[data-project-accordion][open]').forEach((otherDetails) => {
                    if (otherDetails !== details) animateAccordion(otherDetails, false);
                });
            }
            animateAccordion(details, true);
        });
    });

    // -------------------------------------------------------------
    // Universal Top Navbar Profile Dropdown Controller
    // -------------------------------------------------------------
    const profileBtn = document.getElementById('navProfileTrigger');
    const profileMenu = document.getElementById('navProfileMenu');
    if (profileBtn && profileMenu) {
        const scrollWrap = document.getElementById('navDropdownScrollWrap');
        const arrowHint = document.getElementById('navScrollArrowHint');

        const updateScrollHint = () => {
            if (!scrollWrap || !arrowHint) return;
            const canScroll = scrollWrap.scrollHeight > scrollWrap.clientHeight;
            const atBottom = Math.ceil(scrollWrap.scrollTop + scrollWrap.clientHeight) >= scrollWrap.scrollHeight - 8;
            if (canScroll && !atBottom) {
                arrowHint.style.display = 'block';
            } else {
                arrowHint.style.display = 'none';
            }
        };

        if (scrollWrap) {
            scrollWrap.addEventListener('scroll', updateScrollHint, { passive: true });
        }

        window.scrollNavDropdownDown = () => {
            if (scrollWrap) {
                scrollWrap.scrollBy({ top: 90, behavior: 'smooth' });
            }
        };

        const toggleProfileMenu = (open) => {
            const isCurrentlyOpen = profileBtn.getAttribute('aria-expanded') === 'true';
            const shouldOpen = open !== undefined ? open : !isCurrentlyOpen;
            profileBtn.setAttribute('aria-expanded', String(shouldOpen));
            profileMenu.classList.toggle('is-open', shouldOpen);
            if (shouldOpen) {
                setTimeout(updateScrollHint, 60);
            }
        };

        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleProfileMenu();
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!profileBtn.contains(e.target) && !profileMenu.contains(e.target)) {
                toggleProfileMenu(false);
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && profileBtn.getAttribute('aria-expanded') === 'true') {
                toggleProfileMenu(false);
                profileBtn.focus();
            }
        });
    }

    // -------------------------------------------------------------
    // Cyber Alert Auto-Dismiss Controller
    // Alerts stay for reading time, pause on hover, and gracefully fade out
    // -------------------------------------------------------------
    const initAutoDismissAlert = (alertBox) => {
        if (!alertBox || alertBox.dataset.alertInitialized === 'true') return;
        alertBox.dataset.alertInitialized = 'true';

        const dismissDelay = parseInt(alertBox.getAttribute('data-dismiss-delay') || '6000', 10);
        let dismissTimer = null;
        let remainingTime = dismissDelay;
        let startTime = Date.now();

        const dismiss = () => {
            alertBox.classList.add('is-dismissing');
            setTimeout(() => {
                alertBox.remove();
            }, 520);
        };

        const startTimer = () => {
            startTime = Date.now();
            dismissTimer = setTimeout(dismiss, remainingTime);
        };

        const pauseTimer = () => {
            clearTimeout(dismissTimer);
            remainingTime -= (Date.now() - startTime);
            if (remainingTime < 500) remainingTime = 500;
        };

        alertBox.addEventListener('mouseenter', pauseTimer);
        alertBox.addEventListener('mouseleave', startTimer);

        const closeBtn = alertBox.querySelector('.cyber-alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                clearTimeout(dismissTimer);
                dismiss();
            });
        }

        startTimer();
    };

    document.querySelectorAll('.auto-dismiss-alert').forEach(initAutoDismissAlert);

    // -------------------------------------------------------------
    // Global Cyber Dynamic Alert Dispatcher
    // -------------------------------------------------------------
    window.showCyberAlert = (message, type = 'error', targetContainer = null) => {
        let container = targetContainer;
        if (!container) {
            container = document.querySelector('.dashboard-messages-area') || 
                        document.getElementById('message-container') ||
                        document.querySelector('form');
        }
        if (!container) return;

        const alertBox = document.createElement('div');
        alertBox.className = `cyber-alert-box auto-dismiss-alert ${type}`;
        alertBox.setAttribute('data-dismiss-delay', '7500');

        let tagText = '[ TRANSMISSION ]';
        if (type === 'error') {
            tagText = '[ FAILED / SYSTEM ERROR ]';
        } else if (type === 'success') {
            tagText = '[ SUCCESS / CONFIRMED ]';
        } else if (type === 'warning') {
            tagText = '[ WARNING / CAUTION ]';
        }

        alertBox.innerHTML = `
            <span class="cyber-alert-tag">${tagText}</span>
            <span class="cyber-alert-content">${message}</span>
            <button type="button" class="cyber-alert-close" aria-label="Dismiss">&times;</button>
            <div class="cyber-alert-progress"><div class="cyber-alert-progress-fill"></div></div>
        `;

        if (container.tagName === 'FORM') {
            container.parentNode.insertBefore(alertBox, container);
        } else {
            container.prepend(alertBox);
        }

        initAutoDismissAlert(alertBox);
        try {
            alertBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } catch (_) {}
    };

    // -------------------------------------------------------------
    // Cybernetic Button Loading Spinner System
    // Puts an animated circular spinner in buttons during processing
    // -------------------------------------------------------------
    window.setButtonProcessing = (button, customText = null) => {
        if (!button || button.classList.contains('btn-is-processing')) return false;

        button.setAttribute('data-original-html', button.innerHTML);
        const loadingText = customText || button.getAttribute('data-loading-text') || 'Processing Request...';
        
        button.classList.add('btn-is-processing');
        button.setAttribute('aria-busy', 'true');
        button.disabled = true;

        button.innerHTML = `<span class="cyber-btn-spinner" aria-hidden="true"></span><span>${loadingText}</span>`;

        // Safety reset after 15 seconds if navigation did not occur
        setTimeout(() => {
            window.resetButtonProcessing(button);
        }, 15000);
        return true;
    };

    window.resetButtonProcessing = (button) => {
        if (!button || !button.classList.contains('btn-is-processing')) return;
        const originalHtml = button.getAttribute('data-original-html');
        if (originalHtml) {
            button.innerHTML = originalHtml;
        }
        button.classList.remove('btn-is-processing');
        button.removeAttribute('aria-busy');
        button.disabled = false;
    };

    // Attach automatic loading spinner to all form submissions
    document.querySelectorAll('form').forEach((form) => {
        if (form.getAttribute('data-no-spinner') === 'true') return;

        form.addEventListener('submit', function (e) {
            // Respect native validation failure
            if (typeof form.checkValidity === 'function' && !form.checkValidity()) {
                return;
            }

            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                // If button already processing, prevent double-submission
                if (submitBtn.classList.contains('btn-is-processing')) {
                    e.preventDefault();
                    return;
                }

                let text = submitBtn.getAttribute('data-loading-text');
                if (!text) {
                    if (form.id === 'registryWizardForm') {
                        text = 'Deploying Registry Footprint...';
                    } else if (document.getElementById('rootEye') || form.closest('.btn-root')) {
                        text = 'Authenticating Root Clearance...';
                    } else if (document.getElementById('id_username') && document.getElementById('id_password')) {
                        text = 'Authenticating Security Node...';
                    } else if (form.querySelector('input[name="action"][value="update_profile"]')) {
                        text = 'Updating Profile Telemetry...';
                    } else if (form.querySelector('input[name="action"][value="change_password"]')) {
                        text = 'Rotating Security Keyphrase...';
                    } else if (form.querySelector('input[name="action"][value="send_inquiry"]')) {
                        text = 'Transmitting Proposal...';
                    } else if (form.querySelector('input[name="action"][value="add_project"]')) {
                        text = 'Deploying Project to Vault...';
                    } else {
                        text = 'Processing Details...';
                    }
                }
                window.setButtonProcessing(submitBtn, text);
            }
        });
    });
});
