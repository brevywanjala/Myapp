const components = document.querySelectorAll('.bg-white');
    
class ExpandableComponent {
    constructor(container) {
        this.container = container;
        this.contentElement = this.container.querySelector('.expandable-container');
        this.expandIconElement = this.container.querySelector('.expand-icon');
        this.copyIconElement = this.container.querySelector('.copy-icon');
        this.copyFeedbackElement = this.container.querySelector('.copy-feedback');

        this.expandIconElement.addEventListener('click', this.toggleContent.bind(this));
        this.copyIconElement.addEventListener('click', this.copyToClipboard.bind(this));
    }

    toggleContent() {
        this.contentElement.classList.toggle('ml-0');
        this.contentElement.classList.toggle('content-visible');
    }

    copyToClipboard() {
        const sentence = this.contentElement.querySelector('.expandable-content').innerText;
        const tempInput = document.createElement('textarea');
        tempInput.value = sentence;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);

        this.contentElement.classList.add('content-visible');
        this.copyFeedbackElement.style.display = 'block';

        setTimeout(() => {
            this.copyFeedbackElement.style.display = 'none';
        }, 2000);
    }
}

videoContainer.addEventListener('click', event => {
    const clickedExpandIcon = event.target.closest('.expand-icon');
    const clickedCopyIcon = event.target.closest('.copy-icon');
    
    if (clickedExpandIcon) {
        const expandableContainer = clickedExpandIcon.closest('.bg-white');
        new ExpandableComponent(expandableContainer);
    }
    
    if (clickedCopyIcon) {
        const expandableContainer = clickedCopyIcon.closest('.bg-white');
        new ExpandableComponent(expandableContainer);
    }
});

components.forEach(component => new ExpandableComponent(component));