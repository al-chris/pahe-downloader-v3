// Anime Downloader JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Select all episodes functionality
    const selectAllCheckbox = document.getElementById('select-all');
    const episodeCheckboxes = document.querySelectorAll('.episode-checkbox');

    if (selectAllCheckbox && episodeCheckboxes.length > 0) {
        selectAllCheckbox.addEventListener('change', function() {
            episodeCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
                toggleEpisodeCard(checkbox);
            });
        });

        episodeCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                toggleEpisodeCard(this);
                updateSelectAllState();
            });
        });
    }

    function toggleEpisodeCard(checkbox) {
        const card = checkbox.closest('.episode-card');
        if (card) {
            if (checkbox.checked) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        }
    }

    // Episode selection form validation
    const downloadSelectedForm = document.getElementById('download-selected-form');
    const downloadSelectedButton = downloadSelectedForm ? downloadSelectedForm.querySelector('button[type="submit"]') : null;

    // Function to update episode download button state
    function updateEpisodeDownloadButtonState() {
        if (!downloadSelectedButton || !episodeCheckboxes.length) return;

        const checkedCount = document.querySelectorAll('.episode-checkbox:checked').length;
        const hasSelection = checkedCount > 0;

        downloadSelectedButton.disabled = !hasSelection;

        if (hasSelection) {
            downloadSelectedButton.classList.remove('btn-disabled');
            downloadSelectedButton.title = '';
        } else {
            downloadSelectedButton.classList.add('btn-disabled');
            downloadSelectedButton.title = 'Please select at least one episode to download';
        }
    }

    // Update episode button state when checkboxes change
    if (episodeCheckboxes.length > 0) {
        updateEpisodeDownloadButtonState(); // Initial state

        episodeCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateEpisodeDownloadButtonState);
        });

        // Also update when select all changes
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', updateEpisodeDownloadButtonState);
        }
    }

    // Handle episode selection form submission
    if (downloadSelectedForm) {
        downloadSelectedForm.addEventListener('submit', function(e) {
            const checkedCount = document.querySelectorAll('.episode-checkbox:checked').length;

            if (checkedCount === 0) {
                e.preventDefault();
                showAlert('Please select at least one episode to download', 'error');
                return;
            }

            // Disable button to prevent duplicate submission
            if (downloadSelectedButton) {
                downloadSelectedButton.innerHTML = '<div class="spinner"></div> Starting Download...';
                downloadSelectedButton.disabled = true;
                downloadSelectedButton.style.pointerEvents = 'none'; // Extra protection
            }

            // Also disable the back to homepage button
            const backButton = document.querySelector('a[href="/"].btn.btn-secondary');
            if (backButton) {
                backButton.style.pointerEvents = 'none';
                backButton.style.opacity = '0.6';
                backButton.title = 'Download in progress...';
            }
        });
    }

    // Form validation and button state management
    const urlInput = document.getElementById('anime-url');
    const downloadForm = document.getElementById('download-form');
    const downloadButton = downloadForm ? downloadForm.querySelector('button[type="submit"]') : null;

    // Function to validate AnimePahe URL
    function isValidAnimePaheUrl(url) {
        if (!url || !url.trim()) return false;

        const urlPattern = /^https:\/\/animepahe\.(si|ru|com)\/anime\/[^\/]+\/?$/i;
        return urlPattern.test(url.trim());
    }

    // Function to update download button state
    function updateDownloadButtonState() {
        if (!downloadButton || !urlInput) return;

        const url = urlInput.value.trim();
        const isValid = isValidAnimePaheUrl(url);

        downloadButton.disabled = !isValid;

        if (isValid) {
            downloadButton.classList.remove('btn-disabled');
            downloadButton.title = '';
        } else {
            downloadButton.classList.add('btn-disabled');
            downloadButton.title = 'Please enter a valid AnimePahe URL (e.g., https://animepahe.pw/anime/anime-id)';
        }
    }

    // URL input validation
    if (urlInput && downloadForm) {
        // Initial state
        updateDownloadButtonState();

        // Update on input
        urlInput.addEventListener('input', updateDownloadButtonState);

        downloadForm.addEventListener('submit', function(e) {
            const url = urlInput.value.trim();
            console.log('Form submit triggered with URL:', url);

            if (!url) {
                console.log('Validation failed: empty URL');
                e.preventDefault();
                showAlert('Please enter an anime URL', 'error');
                return;
            }

            if (!isValidAnimePaheUrl(url)) {
                console.log('Validation failed: invalid URL format');
                e.preventDefault();
                showAlert('Please enter a valid AnimePahe URL in the format: https://animepahe.pw/anime/anime-id', 'error');
                return;
            }

            console.log('Validation completed, allowing form submission');
            // Disable button to prevent duplicate submission
            if (downloadButton) {
                downloadButton.innerHTML = '<div class="spinner"></div> Processing...';
                downloadButton.disabled = true;
                downloadButton.style.pointerEvents = 'none'; // Extra protection
            }
        });
    }

    // URL input enhancement
    if (urlInput) {
        urlInput.addEventListener('input', function() {
            const url = this.value.trim();

            if (isValidAnimePaheUrl(url)) {
                this.style.borderColor = 'var(--success-color)';
            } else if (url.length > 0) {
                this.style.borderColor = 'var(--warning-color)';
            } else {
                this.style.borderColor = 'var(--border-color)';
            }
        });
    }

    // Alert system
    function showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            <span>${message}</span>
        `;

        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
        }

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Progress simulation for download page
    const progressBar = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');

    if (progressBar && progressText) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                progressText.textContent = 'Download complete! Preparing files...';
            } else {
                progressText.textContent = `Downloading... ${Math.round(progress)}%`;
            }
            progressBar.style.width = `${progress}%`;
        }, 500);
    }

    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading states to buttons (but not form submit buttons)
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            // Don't interfere with form submit buttons - they handle their own loading state
            if (this.type === 'submit' || (this.form && this.type !== 'button')) {
                return;
            }

            if (!this.disabled) {
                const originalText = this.innerHTML;
                this.innerHTML = '<div class="spinner"></div> Processing...';
                this.disabled = true;

                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 10000);
            }
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+A to select all episodes
        if (e.ctrlKey && e.key === 'a' && episodeCheckboxes.length > 0) {
            e.preventDefault();
            const allChecked = Array.from(episodeCheckboxes).every(cb => cb.checked);
            episodeCheckboxes.forEach(checkbox => {
                checkbox.checked = !allChecked;
                toggleEpisodeCard(checkbox);
            });
            updateSelectAllState();
        }
    });

    // Add tooltips
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });

    function showTooltip(e) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = e.target.dataset.tooltip;
        document.body.appendChild(tooltip);

        const rect = e.target.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - 30}px`;
    }

    function hideTooltip() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
});