const number_options = { 
  minimumFractionDigits: 2,
  maximumFractionDigits: 2 
};
document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let table = new DataTable('#entry-table', {
        "scrollY": "60vh",
        "scrollCollapse": true,
        "paging": false,
        columnDefs: [{
            targets: "_all",
            className: 'dt-right',}]
    });

    document.querySelectorAll(".entry-row").forEach(row => {
        let price_noform = row.querySelector("#price-noform");
        let price_form = row.querySelector("#price-form");
        let price_box = row.querySelector("#price-box")
        let price_input = price_form.querySelector("#price-value");
        row.onclick = () => {
            window.open(row.dataset.url, "_blank")
        };
        price_box.onclick = (event) => {
            price_form.style.display = "";
            price_input.focus();
            price_noform.innerHTML = "";
            event.stopPropagation();
        };
        price_form.onsubmit = (event) => {
            const formData = new FormData(event.target);
            price_form.style.display = "none";
            let entrypk = formData.get("entry-pk");
            fetch(`/api/entries/${entrypk}/`, {
                method: "PUT", 
                body: formData,
                headers: {"X-CSRFTOKEN": csrftoken},
            })
            .then(async response => {
                let data = await response.json()
                console.log(data)
                if (!response.ok){
                    alert(`HTTP RESPONSE STATUS ${response.status}\n-----\n${JSON.stringify(data.errors)}`);
                }
                if (data.price){
                    price_noform.innerHTML = `${parseFloat(data.price).toLocaleString("es", number_options)}`;
                    price_input.value = price_noform.innerHTML
                }else{
                    price_noform.innerHTML = "-";
                    price_input.value = "";
                }
                return false;
            })
            .catch(error => {
                console.log(error);
            });
            event.stopPropagation();
            return false;
        }
    });

    // EVENT
    document.querySelector("#register-all").onclick = () => {

        let formData = new FormData();
        document.querySelectorAll(".entry-row").forEach(row => {
            formData.append(row.dataset.pk, "register");
        });
        fetch("/purchases/entries/", {
            method: "POST",
            body: formData,
            headers: {"X-CSRFTOKEN": csrftoken},
        }).then(response => {
            //alert
            location.reload();
        })
        .catch(error => {console.log(error)});
    };

});

