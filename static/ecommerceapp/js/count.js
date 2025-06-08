

document.addEventListener("DOMContentLoaded", function () {
    const counters = document.querySelectorAll(".count");

    function startCounting(counter) {
        const target = parseInt(counter.getAttribute("data-target"));
        let count = 0;
        const increment = Math.ceil(target / 50); // Adjust the speed by changing divisor

        function updateCount() {
            count += increment;
            if (count > target) count = target;
            counter.innerText = count + "+";
            
            if (count < target) {
                setTimeout(updateCount, 50); // Adjust delay to control speed
            }
        }

        updateCount();
    }

    counters.forEach(counter => startCounting(counter));
});
