// Global state
let currentStep = 1;
const totalSteps = 5;
let userData = {
    userId: '',
    sex: '',
    age: '',
    height: '',
    weight: '',
    goal: '',
    bmr: 0,
    calorieGoal: 0
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    generateUserId();
    updateProgress();
    initIntroBanner();
    initScrollBubbleAvoidance();
});

// Generate random User ID
function generateUserId() {
    const randomNum = Math.floor(Math.random() * 9000) + 1000;
    userData.userId = `USER-${randomNum}`;
    document.getElementById('userId').textContent = userData.userId;
}

// Update progress bar
function updateProgress() {
    const progress = (currentStep / totalSteps) * 100;
    document.getElementById('progressFill').style.width = `${progress}%`;
    document.getElementById('currentStep').textContent = currentStep;
    document.getElementById('totalSteps').textContent = totalSteps;
}

// Step navigation
function nextStep() {
    if (currentStep < totalSteps) {
        hideStep(currentStep);
        currentStep++;
        showStep(currentStep);
        updateProgress();
    }
}

function prevStep() {
    if (currentStep > 1) {
        hideStep(currentStep);
        currentStep--;
        showStep(currentStep);
        updateProgress();
    }
}

function showStep(step) {
    const stepElement = document.getElementById(`step${step}`);
    stepElement.classList.add('active');
    
    // Special handling for step 4 (calculation)
    if (step === 4) {
        calculateResults();
    }
    
    // Special handling for step 5 (backend sync)
    if (step === 5) {
        syncToBackend();
    }
}

function hideStep(step) {
    const stepElement = document.getElementById(`step${step}`);
    stepElement.classList.remove('active');
}

// Step 2: Sex selection
function selectSex(sex) {
    userData.sex = sex;
    const buttons = document.querySelectorAll('.toggle-btn');
    buttons.forEach(btn => {
        if (btn.dataset.value === sex) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Step 2: Validation
function validateStep2() {
    const age = document.getElementById('age').value;
    const height = document.getElementById('height').value;
    const weight = document.getElementById('weight').value;
    
    if (!userData.sex) {
        alert('Please select your sex');
        return;
    }
    
    if (!age || age < 13 || age > 120) {
        alert('Please enter a valid age (13-120)');
        return;
    }
    
    if (!height || height < 100 || height > 250) {
        alert('Please enter a valid height (100-250 cm)');
        return;
    }
    
    if (!weight || weight < 30 || weight > 300) {
        alert('Please enter a valid weight (30-300 kg)');
        return;
    }
    
    // Save data
    userData.age = parseInt(age);
    userData.height = parseFloat(height);
    userData.weight = parseFloat(weight);
    
    nextStep();
}

// Step 3: Goal selection
function selectGoal(goal) {
    userData.goal = goal;
    const cards = document.querySelectorAll('.goal-card');
    cards.forEach(card => {
        if (card.dataset.goal === goal) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
    
    // Enable next button
    document.getElementById('step3Next').disabled = false;
}

// Step 3: Validation
function validateStep3() {
    if (!userData.goal) {
        alert('Please select a goal');
        return;
    }
    
    nextStep();
}

// Step 4: Calculate BMR and Calorie Goal
function calculateResults() {
    // Calculate BMR using Mifflin-St Jeor Equation
    let bmr;
    const W = userData.weight; // Weight in kg
    const H = userData.height; // Height in cm
    const A = userData.age; // Age in years
    
    if (userData.sex === 'male') {
        // Men: 10*W + 6.25*H - 5*A + 5
        bmr = (10 * W) + (6.25 * H) - (5 * A) + 5;
    } else {
        // Women: 10*W + 6.25*H - 5*A - 161
        bmr = (10 * W) + (6.25 * H) - (5 * A) - 161;
    }
    
    // Calculate TDEE (Base TDEE = BMR * 1.2)
    const baseTDEE = bmr * 1.2;
    
    // Apply modifier based on goal
    let calorieGoal;
    if (userData.goal === 'lose') {
        calorieGoal = baseTDEE - 500; // Deficit for weight loss
    } else if (userData.goal === 'maintain') {
        calorieGoal = baseTDEE; // Maintain current weight
    } else if (userData.goal === 'gain') {
        calorieGoal = baseTDEE + 500; // Surplus for muscle gain
    }
    
    // Round to nearest integer
    userData.bmr = Math.round(bmr);
    userData.calorieGoal = Math.round(calorieGoal);
    
    // Display results
    document.getElementById('bmrValue').textContent = userData.bmr.toLocaleString();
    document.getElementById('calorieGoalValue').textContent = userData.calorieGoal.toLocaleString();
}

// Step 5: Backend Synchronization
async function syncToBackend() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    
    // Show loading
    loadingSpinner.style.display = 'block';
    successMessage.style.display = 'none';
    errorMessage.style.display = 'none';
    
    // Prepare data
    const payload = {
        userId: userData.userId,
        age: userData.age,
        sex: userData.sex,
        height: userData.height,
        weight: userData.weight,
        goal: userData.goal,
        bmr: userData.bmr,
        calorieGoal: userData.calorieGoal
    };
    
    try {
        // Send POST request to backend
        // Update this URL to match your backend endpoint
        const response = await fetch('http://localhost:8000/api/init-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Success: redirect directly to homepage
        loadingSpinner.style.display = 'none';
        successMessage.style.display = 'block';
        window.location.href = '../Mainpage/index.html';
        
    } catch (error) {
        console.error('Error syncing to backend:', error);
        
        // Show error message
        loadingSpinner.style.display = 'none';
        errorMessage.style.display = 'block';
        document.getElementById('errorText').textContent = 
            'Failed to sync with server. Please check your connection and try again.';
        
        // For development/testing: Allow user to continue even if backend is offline
        // Uncomment the following lines if you want to allow offline testing:
        /*
        setTimeout(() => {
            window.location.href = '../Mainpage/index.html';
        }, 3000);
        */
    }
}

// Retry sync
function retrySync() {
    syncToBackend();
}

// Input validation helpers
document.getElementById('age')?.addEventListener('input', (e) => {
    const value = parseInt(e.target.value);
    if (value < 13 || value > 120) {
        e.target.style.borderColor = '#ef4444';
    } else {
        e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
});

document.getElementById('height')?.addEventListener('input', (e) => {
    const value = parseFloat(e.target.value);
    if (value < 100 || value > 250) {
        e.target.style.borderColor = '#ef4444';
    } else {
        e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
});

document.getElementById('weight')?.addEventListener('input', (e) => {
    const value = parseFloat(e.target.value);
    if (value < 30 || value > 300) {
        e.target.style.borderColor = '#ef4444';
    } else {
        e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
});

// Scroll bubble avoidance
function initScrollBubbleAvoidance() {
    const bubble = document.getElementById('scrollBubble');
    if (!bubble) return;

    const maxOffset = 120; // max pixels bubble can run from center
    const safeRadius = 180; // distance where bubble starts to move

    function clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }

    function resetTransform() {
        bubble.style.transform = 'translate(-50%, 0)';
    }

    function handleMove(x, y) {
        const rect = bubble.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const dx = centerX - x;
        const dy = centerY - y;
        const distance = Math.hypot(dx, dy);

        if (distance < safeRadius) {
            const force = (safeRadius - distance) / safeRadius;
            const moveX = clamp((dx / (distance || 1)) * force * maxOffset, -maxOffset, maxOffset);
            const moveY = clamp((dy / (distance || 1)) * force * maxOffset, -maxOffset, maxOffset);
            bubble.style.transform = `translate(-50%, 0) translate(${moveX}px, ${moveY}px)`;
        } else {
            resetTransform();
        }
    }

    document.addEventListener('mousemove', (e) => handleMove(e.clientX, e.clientY));
    document.addEventListener('touchmove', (e) => {
        const touch = e.touches[0];
        if (touch) handleMove(touch.clientX, touch.clientY);
    }, { passive: true });
}

// Intro Banner Scroll Handler
function initIntroBanner() {
    const introBanner = document.getElementById('introBanner');
    const mainContainer = document.getElementById('mainContainer');
    const backgroundGradient = document.querySelector('.background-gradient');
    let hasScrolled = false;
    
    // Handle scroll event
    function handleScroll() {
        const scrollY = window.scrollY || window.pageYOffset;
        const scrollThreshold = 100; // Start transition after 100px scroll
        
        if (scrollY > scrollThreshold && !hasScrolled) {
            hasScrolled = true;
            introBanner.classList.add('scrolled');
            backgroundGradient.classList.add('visible');
            mainContainer.classList.add('visible');
        } else if (scrollY <= scrollThreshold && hasScrolled) {
            hasScrolled = false;
            introBanner.classList.remove('scrolled');
            backgroundGradient.classList.remove('visible');
            mainContainer.classList.remove('visible');
        }
    }
    
    // Listen for scroll events
    window.addEventListener('scroll', handleScroll);
    
    // Initial check
    handleScroll();
}

// Initialize Orbital Lines with Cursor Interaction
function initOrbitalLines() {
    const canvas = document.getElementById('orbitalCanvas');
    const ctx = canvas.getContext('2d');
    let mouseX = 0;
    let mouseY = 0;
    let animationFrame;
    
    // Orbital lines configuration
    const orbitalLines = [];
    const numLines = 12;
    
    // Initialize orbital lines with random properties
    for (let i = 0; i < numLines; i++) {
        orbitalLines.push({
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            radius: 50 + Math.random() * 200,
            speed: 0.0002 + Math.random() * 0.0003,
            angle: Math.random() * Math.PI * 2,
            size: 1 + Math.random() * 2,
            opacity: 0.3 + Math.random() * 0.4
        });
    }
    
    // Set canvas size
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        drawOrbitalLines();
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Draw orbital lines
    function drawOrbitalLines() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const time = Date.now() * 0.001;
        
        orbitalLines.forEach((line, index) => {
            // Calculate mouse influence
            const dx = mouseX - line.x;
            const dy = mouseY - line.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const influence = Math.max(0, 1 - distance / 400); // 400px influence radius
            
            // Update angle with speed and mouse influence
            line.angle += line.speed + (influence * 0.002);
            
            // Calculate orbital position
            const centerX = line.x + Math.cos(line.angle) * line.radius;
            const centerY = line.y + Math.sin(line.angle) * line.radius;
            
            // Apply mouse attraction
            const mouseInfluenceX = dx * influence * 0.5;
            const mouseInfluenceY = dy * influence * 0.5;
            
            const finalX = centerX + mouseInfluenceX;
            const finalY = centerY + mouseInfluenceY;
            
            // Draw the orbital line
            ctx.beginPath();
            ctx.strokeStyle = `rgba(26, 26, 26, ${line.opacity + influence * 0.3})`;
            ctx.lineWidth = line.size + (influence * 2);
            ctx.lineCap = 'round';
            
            // Draw curved orbital path
            const points = 60;
            for (let i = 0; i <= points; i++) {
                const t = i / points;
                const angle = line.angle + (t * Math.PI * 2);
                const x = line.x + Math.cos(angle) * line.radius + (dx * influence * 0.5 * t);
                const y = line.y + Math.sin(angle) * line.radius + (dy * influence * 0.5 * t);
                
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            
            ctx.stroke();
            
            // Draw additional smaller orbits for depth
            if (line.radius > 100) {
                ctx.beginPath();
                ctx.strokeStyle = `rgba(26, 26, 26, ${(line.opacity * 0.5) + influence * 0.2})`;
                ctx.lineWidth = line.size * 0.5;
                const innerRadius = line.radius * 0.6;
                
                for (let i = 0; i <= points; i++) {
                    const t = i / points;
                    const angle = line.angle + (t * Math.PI * 2);
                    const x = line.x + Math.cos(angle) * innerRadius + (dx * influence * 0.3 * t);
                    const y = line.y + Math.sin(angle) * innerRadius + (dy * influence * 0.3 * t);
                    
                    if (i === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                }
                ctx.stroke();
            }
        });
    }
    
    // Track mouse position
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });
    
    // Animate
    function animate() {
        drawOrbitalLines();
        animationFrame = requestAnimationFrame(animate);
    }
    
    animate();
}

