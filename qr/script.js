// Set the initial time in seconds
let timeInSeconds = 180; // 3 minutes

// Function to update the countdown
function updateCountdown() {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = timeInSeconds % 60;

    // Format the time as "mm:ss"
    const formattedTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

    // Update the displayed time
    document.getElementById('countdown').innerHTML = `<span>${formattedTime}</span><br />`;

    // Check if time is up
    if (timeInSeconds === 0) {
        // Get the current URL
        var currentUrl = window.location.href;

        // Construct the new URL by appending the current URL as a parameter
        var newUrl = "/qr/expire.php?url=" + encodeURIComponent(currentUrl);

        // Redirect to the new URL
        window.location.href = newUrl;
    } else {
        // Decrement the time
        timeInSeconds--;
    }
}

// Call the updateCountdown function every second
setInterval(updateCountdown, 1000);

// API
const apiUrl = 'https://api-bakong.nbc.gov.kh/v1/check_transaction_by_md5';
const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiZWI3ZTk4MTE4Zjk2NDRkNCJ9LCJpYXQiOjE3NDI5ODI0NDUsImV4cCI6MTc1MDc1ODQ0NX0.OEDVGLmdepoFqKlG3f4AFnuAKEbKIKeiSv15pGjfJrk'

// Function to check the API and redirect if successful
async function checkAPIAndRedirect() {
    const data = JSON.stringify({ md5: '<?php echo $md5; ?>' });

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: data,
        });

        const jsonResponse = await response.json();

        if (jsonResponse.responseCode === 0) {
            // Redirect to the successful PHP page
            window.location.href = '/qr/tg.php?transaction=<?php echo $transaction; ?>';
        }
    } catch (error) {
        console.error('Error during API request:', error);
    }
}

// Call the function every second
setInterval(checkAPIAndRedirect, 1000);
