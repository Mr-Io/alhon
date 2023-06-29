const number_options = {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
};

// append client form

document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    function create_client_price_cell(pk, price) {
        // clone
        let formrow = document.querySelector("#formrow-forclone").cloneNode(true);
        // variables
        let client_price_noform = formrow.querySelector("#client-price-noform");
        let client_price_form = formrow.querySelector("#client-price-form");
        let client_price_input = formrow.querySelector("#client-price-input");
        // update values
        console.log(`pk: ${pk}, price: ${price}`);
        client_price_noform.innerHTML = price ? parseFloat(price).toLocaleString("es", number_options) : "-";
        client_price_input.value = price;
        // add events
        client_price_noform.onclick = () => {
            client_price_noform.style.display = "none";
            client_price_form.style.display = "";
            client_price_input.focus();
        };
        client_price_form.onsubmit = (event) => {
            const formdata = new FormData(event.target);
            let values = { price: formdata.get("client-price") };
            // send data
            fetch(`/api/exits/${pk}/`, {
                method: "PUT",
                headers: {
                    "X-CSRFTOKEN": csrftoken,
                    "Content-Type": "application/json",
                    Accept: "application/json",
                },
                body: JSON.stringify(values),
            })
                .then(async (response) => {
                    let data = await response.json();
                    if (!response.ok) {
                        alert(`HTTP RESPONSE STATUS ${response.status}\n-----\n${JSON.stringify(data.errors)}`);
                    }
                    if (data.price) {
                        client_price_noform.innerHTML = `${parseFloat(data.price).toLocaleString("es", number_options)}`;
                        client_price_input.value = client_price_noform.innerHTML;
                    } else {
                        client_price_noform.innerHTML = "-";
                        client_price_input.value = "";
                    }
                    return false;
                })
                .catch((error) => {
                    console.log(error);
                });
            // change values
            client_price_noform.style.display = "";
            client_price_form.style.display = "none";
            return false;
        };
        return formrow;
    }

    let agrofood_form = document.querySelector("#agrofood-form");
    let agrofood_pk = document.querySelector("#agrofood-pk");

    agrofood_pk.oninput = () => {
        agrofood_form.submit();
    };

    document.querySelectorAll(".sale-row").forEach((row) => {
        console.log(row);
        // variables
        let client_price_noform = row.querySelector("#client-price-noform");
        let client_price_form = row.querySelector("#client-price-form");
        let client_price_input = row.querySelector("#client-price-input");

        // add change client price events
        if (client_price_form) {
            client_price_noform.onclick = () => {
                client_price_noform.style.display = "none";
                client_price_form.style.display = "";
                client_price_input.focus();
            };
            client_price_form.onsubmit = (event) => {
                const formdata = new FormData(event.target);
                let values = { price: formdata.get("client-price") };
                // send data
                fetch(`/api/exits/${formdata.get("exit-pk")}/`, {
                    method: "PUT",
                    headers: {
                        "X-CSRFTOKEN": csrftoken,
                        "Content-Type": "application/json",
                        Accept: "application/json",
                    },
                    body: JSON.stringify(values),
                })
                    .then(async (response) => {
                        let data = await response.json();
                        console.log(data);
                        if (!response.ok) {
                            alert(`HTTP RESPONSE STATUS ${response.status}\n-----\n${JSON.stringify(data.errors)}`);
                        }
                        if (data.price) {
                            client_price_noform.innerHTML = `${parseFloat(data.price).toLocaleString("es", number_options)}`;
                            client_price_input.value = client_price_noform.innerHTML;
                        } else {
                            client_price_noform.innerHTML = "-";
                            client_price_input.value = "";
                        }
                        return false;
                    })
                    .catch((error) => {
                        console.log(error);
                    });

                // change values
                client_price_noform.style.display = "";
                client_price_form.style.display = "none";
                return false;
            };
        }
    });

    // Añadir Venta logic
    document.querySelectorAll(".main-row-exit").forEach((row) => {
        // variables
        let add_sale_btn = row.querySelector("#add-sale-btn");
        let add_sale_form = row.querySelector("#add-sale-form");
        let pk_cell = row.querySelector("#pk-cell");
        let supplier_cell = row.querySelector("#supplier-cell");
        let pending_packages_cell = row.querySelector("#pending-packages-cell");
        let pending_cell = row.querySelector("#pending-cell");
        let price_cell = row.querySelector("#price-cell");
        let client_select = row.querySelector("#client-select");
        let supplier_price_noform = row.querySelector("#supplier-price-noform");
        let supplier_price_form = row.querySelector("#supplier-price-form");
        let supplier_price_input = row.querySelector("#supplier-price-input");
        // add change supplier price events
        if (supplier_price_form) {
            supplier_price_noform.onclick = () => {
                supplier_price_noform.style.display = "none";
                supplier_price_form.style.display = "";
                supplier_price_input.focus();
            };
            supplier_price_form.onsubmit = (event) => {
                const formdata = new FormData(event.target);
                let values = { price: formdata.get("supplier-price") };
                // send data
                fetch(`/api/entries/${formdata.get("entry-pk")}/`, {
                    method: "PUT",
                    headers: {
                        "X-CSRFTOKEN": csrftoken,
                        "Content-Type": "application/json",
                        Accept: "application/json",
                    },
                    body: JSON.stringify(values),
                })
                    .then(async (response) => {
                        let data = await response.json();
                        console.log(data);
                        if (!response.ok) {
                            alert(`HTTP RESPONSE STATUS ${response.status}\n-----\n${JSON.stringify(data.errors)}`);
                        }
                        if (data.price) {
                            supplier_price_noform.innerHTML = `${parseFloat(data.price).toLocaleString("es", number_options)}`;
                            supplier_price_input.value = supplier_price_noform.innerHTML;
                        } else {
                            supplier_price_noform.innerHTML = "-";
                            supplier_price_input.value = "";
                        }
                        return false;
                    })
                    .catch((error) => {
                        console.log(error);
                    });

                // change values
                supplier_price_noform.style.display = "";
                supplier_price_form.style.display = "none";
                return false;
            };
        }

        // add add sale events
        if (add_sale_btn) {
            add_sale_btn.onclick = () => {
                add_sale_form.style.display = "";
                add_sale_btn.style.display = "none";
            };
        }
        if (add_sale_form) {
            let pending_input = row.querySelector("#pending-input");
            let pending_packages_input = row.querySelector("#pending-packages-input");
            let price_input = row.querySelector("#price-input");
            // add values
            pending_input.value = parseInt(pending_cell.innerHTML);
            pending_packages_input.value = parseInt(pending_packages_cell.innerHTML);
            pending_packages_input.oninput = () => {
                let ratio = pending_cell.innerHTML / pending_packages_cell.innerHTML;
                pending_input.value = Math.round(ratio * pending_packages_input.value);
            };
            add_sale_form.onsubmit = (event) => {
                const formdata = new FormData(event.target);
                add_sale_form.style.display = "none";
                add_sale_btn.style.display = "";
                if (client_select.value && pending_input.value) {
                    // send values
                    values = {
                        client: client_select.value,
                        entry: formdata.get("entry"),
                        weight: pending_input.value,
                        price: price_input.value,
                        packaging_transaction: {
                            packaging: formdata.get("packaging-type"),
                            agent: client_select.value,
                            number: -pending_packages_input.value,
                        },
                    };
                    console.log(values);
                    fetch("/api/exits/", {
                        method: "POST",
                        headers: {
                            "X-CSRFTOKEN": csrftoken,
                            "Content-Type": "application/json",
                            Accept: "application/json",
                        },
                        body: JSON.stringify(values),
                    })
                        .then((response) => response.json())
                        .then((data) => {
                            // create new row
                            let new_row = document.createElement("tr");
                            let new_client = document.createElement("td");
                            let new_bultos = document.createElement("td");
                            let new_kg = document.createElement("td");
                            let new_precio = document.createElement("td");
                            new_client.innerHTML = client_select.options[client_select.selectedIndex].text;
                            new_bultos.innerHTML = pending_packages_input.value ? pending_packages_input.value : "-";
                            new_kg.innerHTML = pending_input.value;
                            new_precio.innerHTML = price_input.value ? price_input.value : "-";
                            new_row.appendChild(new_client);
                            new_row.appendChild(new_bultos);
                            new_row.appendChild(new_kg);
                            console.log(data);
                            new_row.appendChild(create_client_price_cell(new_row, data.pk, data.price));
                            // add new row
                            row.parentNode.insertBefore(new_row, row.nextSibling);
                            pk_cell.rowSpan += 1;
                            supplier_cell.rowSpan += 1;
                            pending_packages_cell.rowSpan += 1;
                            pending_cell.rowSpan += 1;
                            price_cell.rowSpan += 1;
                            if (row.classList.contains("table-danger")) {
                                new_row.classList.add("table-danger");
                            }
                            // update values
                            pending_cell.innerHTML -= pending_input.value;
                            pending_input.max = pending_cell.innerHTML;
                            pending_packages_cell.innerHTML -= pending_packages_input.value;
                            pending_packages_input.max = pending_packages_cell.innerHTML;
                            client_select.value = "";
                            pending_input.value = pending_cell.innerHTML;
                            pending_packages_input.value = pending_packages_cell.innerHTML;
                            // Ddelete row if necessary
                            if (pending_cell.innerHTML === "0") {
                                add_sale_btn.parentNode.parentNode.style.display = "none";
                            }
                            console.log(data);
                        })
                        .catch((errors) => {
                            console.log(errors);
                        });
                } else {
                    alert("No se puede hacer una venta si no se selecciona el cliente o el número de kg.");
                }
                return false;
            };
        }
    });
});
