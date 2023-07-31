let supplierdata;

document.addEventListener("DOMContentLoaded", () => {

    // ########## VARIABLES ##########
    const agent_pk = document.querySelector("#agent-pk");

    const submit_btn = document.querySelector("#submit-btn");
    const print_btn = document.querySelector("#print-btn")

    const balance_table = document.querySelector("#balance-table");
    const agent_name = document.querySelector("#agent-name");
    const balance_table_body = document.querySelector("#balance-table-body");

    const transaction_pdf_anchor = document.querySelector("#transaction-pdf-anchor");

    let mov_label_row = document.querySelector("#mov-label-row");
    let input_row = document.querySelector("#movement-input-row");
    let inputid = 0;
    let inputcount = 0;
    let add_mov_btn = document.querySelector("#add-mov-btn")

    // ########## FUNCTIONS ##########
    function addmovement() {
        if (inputcount == 0){
            mov_label_row.style.display = "";
            submit_btn.style.display = "";
        }
        inputid += 1;
        inputcount += 1;
        let next_input_row = input_row.cloneNode(true);
        next_input_row.style.display = "";
        let close_row_btn = next_input_row.querySelector("#close-row-btn");
        let packaging_pk = next_input_row.querySelector("#packaging-pk");
        let num_packages = next_input_row.querySelector("#num-packages");
        packaging_pk.setAttribute("required", "");
        num_packages.setAttribute("required", "");
        close_row_btn.onclick = () => {
            inputcount -= 1;
            if (inputcount == 0){
                mov_label_row.style.display = "none";
                submit_btn.style.display = "none";
            }
            next_input_row.remove();
        }
        input_row.parentNode.insertBefore(next_input_row, input_row);
    }
    // ########## EVENT LISTENERS ##########
    add_mov_btn.onclick = addmovement;

    agent_pk.oninput = () => {
        balance_table.style.display = "none";
        balance_table_body.innerHTML = "";
        // show table after it is updated
        agent_name.innerHTML = agent_pk.options[agent_pk.selectedIndex].text;
        fetch(`/api/agent/${agent_pk.value}/packaging-balance/`)
        .then(response => response.json())
        .then(data => {
            // do something with data
            data.forEach((element) => {
                let row = document.createElement("tr");
                let c1 = document.createElement("td");
                let c2 = document.createElement("td");
                c1.innerHTML = element.name;
                c2.innerHTML = element.balance;
                row.appendChild(c1);
                row.appendChild(c2);
                balance_table_body.appendChild(row);
            });
            // show table again
            balance_table.style.display = "";
        })
        .catch(error => { console.log(error)});
    };

    if (transaction_pdf_anchor){
        window.open(transaction_pdf_anchor.getAttribute("href"));
    }
    
});

