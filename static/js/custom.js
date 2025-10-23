// custom.js - Safe JavaScript enhancements

document.addEventListener('DOMContentLoaded', function() {
    initSafeAnimations();
    initCartInteractions();
    initBackToTop();
    initFormValidations();
});

// Safe animations that won't break layout
function initSafeAnimations() {
    // Animate elements when they come into view
    const animatedElements = document.querySelectorAll('.book-card, .feature-icon');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Cart interactions
function initCartInteractions() {
    // Cart quantity controls
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.value < 1) this.value = 1;
            if (this.value > parseInt(this.max)) this.value = this.max;
        });
    });
    
    // Add loading state to add-to-cart buttons
    const addToCartButtons = document.querySelectorAll('a[href*="add_to_cart"]');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading-spinner"></span> Adding...';
            this.classList.add('loading');
            
            // Revert after 3 seconds if still on same page
            setTimeout(() => {
                this.innerHTML = originalText;
                this.classList.remove('loading');
            }, 3000);
        });
    });
}

// Back to top button
function initBackToTop() {
    // Create back to top button
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTop.className = 'btn btn-primary-custom back-to-top';
    backToTop.setAttribute('aria-label', 'Back to top');
    
    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    document.body.appendChild(backToTop);
    
    // Show/hide based on scroll
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTop.style.display = 'block';
        } else {
            backToTop.style.display = 'none';
        }
    });
}

// Form validations
function initFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
    
    // Real-time validation
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.hasAttribute('required') && !this.value.trim()) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
}

// Utility functions
const BookHub = {
    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },
    
    // Debounce function for search
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Show notification
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '1060';
        notification.style.minWidth = '300px';
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
};

// Make utility functions globally available
window.BookHub = BookHub;

// Safe search enhancement
function initSearchEnhancement() {
    const searchInput = document.querySelector('input[name="query"]');
    
    if (searchInput) {
        searchInput.addEventListener('input', BookHub.debounce(function() {
            this.classList.add('searching');
            setTimeout(() => {
                this.classList.remove('searching');
            }, 500);
        }, 300));
    }
}

// Initialize search enhancement
initSearchEnhancement();