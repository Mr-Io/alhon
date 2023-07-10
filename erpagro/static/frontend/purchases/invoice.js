const number_options = {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
};

// append client form

document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    let table = new DataTable("#entrynotes-table", {
        searching: false,
        info: false,
        paging: false,
        orderFixed: [[2, "asc"]],
        fixedHeader: true,
        rowGroup: {
            dataSrc: (row) => {
                let base = row[3];
                return base;
            },
        },
        //stateSave: true,
        //scrollY: '70vh',
        //scrollCollapse: true,
    });

    // variables
    let daterange_form = document.querySelector("#daterange-form");
    let datefrom_input = document.querySelector("#datefrom-input");
    let dateto_input = document.querySelector("#dateto-input");

    let total_amount_text = document.querySelector("#total-amount-text");

    let supplier_select = document.querySelector("#supplier-select");

    let submit_input = document.querySelector("#submit-input");

    // functions 
    function compute_total_amount_text() {
        let total = 0;
        submit_input.setAttribute("disabled", ""); 
        document.querySelectorAll(".entrynote-pk-checkbox").forEach(checkbox => {
            if (checkbox.checked) {
                submit_input.removeAttribute("disabled");
                total += parseFloat(checkbox.dataset.baseAmount.replace(',', '.'));
            }
        })
        total_amount_text.innerHTML = `Importe Base Factura: ${total.toLocaleString("es", number_options)} €`;
    }

    // events
    if (total_amount_text) {
        compute_total_amount_text();
        document.querySelectorAll(".entrynote-pk-checkbox").forEach(checkbox => {
            checkbox.oninput = () => {
                compute_total_amount_text();
            };
        });
    }
    daterange_form.onsubmit = () => {
        if (supplier_select && supplier_select.value) {
            window.location.search = `datefrom=${datefrom_input.value}&dateto=${dateto_input.value}&supplier=${supplier_select.value}`;
        } else {
            window.location.search = `datefrom=${datefrom_input.value}&dateto=${dateto_input.value}`;
        }
        return false;
    };
    if (supplier_select) {
        supplier_select.oninput = daterange_form.onsubmit;
    }
});
