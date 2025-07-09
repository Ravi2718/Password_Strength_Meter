document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.getElementById('toggleVisibility');
    const bars = Array.from(document.querySelectorAll('.bar-segment'));
    const ratingText = document.getElementById('rating');
    const remarksList = document.getElementById('remarks');
    const crackTimeText = document.getElementById('crack-time');
    let debounceTimer;

    // Password visibility toggle
    toggleBtn.addEventListener('click', () => {
        const isPassword = passwordInput.type === 'password';
        passwordInput.type = isPassword ? 'text' : 'password';
        toggleBtn.innerHTML = isPassword ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
    });

    // Strength check with debouncing
    passwordInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        
        // Show loading state
        bars.forEach(bar => bar.classList.add('loading'));
        
        debounceTimer = setTimeout(async () => {
            const password = passwordInput.value.trim();
            
            if (!password) {
                resetMeter();
                return;
            }
            
            try {
                const response = await fetch('/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ password })
                });
                
                if (!response.ok) throw new Error('Network error');
                
                const result = await response.json();
                updateMeter(result);
            } catch (error) {
                console.error('Error:', error);
                ratingText.textContent = 'Error checking password';
            } finally {
                bars.forEach(bar => bar.classList.remove('loading'));
            }
        }, 300);
    });

    function resetMeter() {
        bars.forEach(bar => {
            bar.className = 'bar-segment';
        });
        ratingText.textContent = 'Strength: None';
        crackTimeText.textContent = '';
        remarksList.innerHTML = '<li>Password requirements will appear here</li>';
    }

    function updateMeter(result) {
        // Reset all bars
        bars.forEach(bar => {
            bar.className = 'bar-segment';
        });

        // Activate the appropriate number of bars with correct class
        const strengthClass = result.rating.toLowerCase().replace(' ', '-');
        for (let i = 0; i < result.strength; i++) {
            if (bars[i]) {
                bars[i].classList.add(strengthClass);
            }
        }

        // Update text displays
        ratingText.textContent = `Strength: ${result.rating}`;
        crackTimeText.textContent = `Crack time: ${result.crack_time}`;
        
        // Only show remarks for weak/medium passwords
        if (result.rating === "Weak" || result.rating === "Very Weak" || result.rating === "Medium") {
            if (result.remarks && result.remarks.length > 0) {
                remarksList.innerHTML = result.remarks.map(r => 
                    `<li><i class="fas fa-exclamation-circle"></i> ${r}</li>`
                ).join('');
            } else {
                remarksList.innerHTML = '<li>No specific recommendations</li>';
            }
        } else {
            remarksList.innerHTML = '<li><i class="fas fa-check-circle"></i> Strong password!</li>';
        }
    }
});