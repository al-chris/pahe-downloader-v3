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

    function updateSelectAllState() {
        const checkedCount = document.querySelectorAll('.episode-checkbox:checked').length;
        const totalCount = episodeCheckboxes.length;

        if (selectAllCheckbox) {
            selectAllCheckbox.checked = checkedCount === totalCount;
            selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
        }
    }

    // Form validation
    const urlInput = document.getElementById('anime-url');
    const downloadForm = document.getElementById('download-form');

    if (urlInput && downloadForm) {
        downloadForm.addEventListener('submit', function(e) {
            const url = urlInput.value.trim();
            if (!url) {
                e.preventDefault();
                showAlert('Please enter an anime URL', 'error');
                return;
            }

            if (!url.includes('animepahe.si')) {
                e.preventDefault();
                showAlert('Please enter a valid AnimePahe URL', 'warning');
                return;
            }

            // Show loading state
            const submitBtn = downloadForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<div class="spinner"></div> Processing...';
                submitBtn.disabled = true;
            }
        });
    }

    // URL input enhancement
    if (urlInput) {
        urlInput.addEventListener('input', function() {
            const url = this.value.trim();
            if (url.includes('animepahe.si/anime/')) {
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

    // Add loading states to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && !this.disabled) {
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