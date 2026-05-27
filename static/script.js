// SEARCH FILTER

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const searchInput =
        document.getElementById(
            "searchInput"
        );

        const rows =
        document.querySelectorAll(
            "#studentTable tr"
        );

        searchInput.addEventListener(
            "keyup",
            function () {

                const filter =
                searchInput.value.toLowerCase();

                rows.forEach(row => {

                    const name =
                    row.cells[0].innerText.toLowerCase();

                    if(name.includes(filter)){

                        row.style.display = "";

                    } else {

                        row.style.display = "none";
                    }
                });
            }
        );

        // DARK MODE

        const themeToggle =
        document.getElementById(
            "themeToggle"
        );

        themeToggle.addEventListener(
            "click",
            () => {

                document.body.classList.toggle(
                    "dark-mode"
                );

                if(
                    document.body.classList.contains(
                        "dark-mode"
                    )
                ){

                    themeToggle.innerText =
                    "Light Mode";

                } else {

                    themeToggle.innerText =
                    "Dark Mode";
                }
            }
        );
    }
);
// FILTER SYSTEM

function filterStudents(type){

    const rows =
    document.querySelectorAll(
        "#studentTable tr"
    );

    rows.forEach(row => {

        const prediction =
        row.dataset.prediction;

        const attendance =
        parseInt(row.dataset.attendance);

        if(type === 'all'){

            row.style.display = "";

        }

        else if(
            type === 'pass' &&
            prediction === 'Pass'
        ){

            row.style.display = "";

        }

        else if(
            type === 'fail' &&
            prediction === 'Fail'
        ){

            row.style.display = "";

        }

        else if(
            type === 'attendance' &&
            attendance < 75
        ){

            row.style.display = "";

        }

        else {

            row.style.display = "none";
        }
    });
}
// LIVE COUNTERS

const counters =
document.querySelectorAll(
    '.counter'
);

counters.forEach(counter => {

    counter.innerText = '0';

    const updateCounter = () => {

        const target =
        +counter.getAttribute(
            'data-target'
        );

        const count =
        +counter.innerText;

        const increment =
        target / 50;

        if(count < target){

            counter.innerText =
            `${Math.ceil(
                count + increment
            )}`;

            setTimeout(
                updateCounter,
                30
            );

        } else {

            counter.innerText =
            target;
        }
    };

    updateCounter();
});
// REAL TIME TOAST

window.onload = () => {

    const toastLiveExample =
    document.getElementById(
        'liveToast'
    );

    if(toastLiveExample){

        const toast =
        new bootstrap.Toast(
            toastLiveExample
        );

        toast.show();
    }
};