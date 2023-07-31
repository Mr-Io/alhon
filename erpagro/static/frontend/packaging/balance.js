let supplierdata;

document.addEventListener("DOMContentLoaded", () => {

    // ########## VARIABLES ##########
    const agent_pk = document.querySelector("#agent-pk");

    const balance_table = document.querySelector("#balance-table");
    const agent_name = document.querySelector("#agent-name");
    const balance_table_body = document.querySelector("#balance-table-body");

    const submit_btn = document.querySelector("#submit-btn");

    let input_saldo_list = null; 

    const new_page_anchor = document.querySelector("#new-page-anchor");

    // ########## FUNCTIONS ##########
    function update_submit () {
        let count = 0;
        input_saldo_list.forEach((element) => {
            if (element.dataset.original_balance != element.value){
                count += 1;
                element.style.color = "red";
            }else{
                element.style.color = "black";
            }
        });
        if (count == 0){
            submit_btn.setAttribute("hidden", "");
        }else{
            submit_btn.removeAttribute("hidden");
        }
    };

    // ########## EVENT LISTENERS ##########
    agent_pk.oninput = () => {
        balance_table.style.display = "none";
        balance_table_body.innerHTML = "";
        // show table after it is updated
        agent_name.innerHTML = agent_pk.options[agent_pk.selectedIndex].text;
        fetch(`/api/agent/${agent_pk.value}/packaging-balance/`)
        .then(response => response.json())
        .then(data => {
            submit_btn.setAttribute("hidden", "");
            // do something with data
            data.forEach((element) => {
                console.log(element);
                let row = document.createElement("tr");
                balance_table_body.appendChild(row);

                let c1 = document.createElement("td");
                row.appendChild(c1);
                c1.innerHTML = element.name;

                let c2 = document.createElement("td");
                row.appendChild(c2);
                let isaldo = document.createElement("input");
                c2.appendChild(isaldo)
                isaldo.setAttribute("type", "number");
                isaldo.setAttribute("name", element.pk);
                isaldo.setAttribute("class", "form-control col-8 input-saldo");
                isaldo.setAttribute("step", "1");
                isaldo.setAttribute("value", element.balance);
                isaldo.dataset.original_balance = element.balance;
                isaldo.oninput = update_submit;
            });
            input_saldo_list = document.querySelectorAll(".input-saldo");
            // show table again
            balance_table.style.display = "";
        })
        .catch(error => { console.log(error)});
    };

        // events
    if (new_page_anchor){
        window.open(new_page_anchor.getAttribute("href"));
    }
});

