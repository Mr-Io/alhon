let supplierdata;

document.addEventListener("DOMContentLoaded", () => {

    // ########## VARIABLES ##########
    let formdiv = document.querySelector("#formdiv");

    const supplier_pk = document.querySelector("#supplier-pk");
    const carrier_pk = document.querySelector("#carrier-pk");
    const carrier_price = document.querySelector("#carrier-price");
    let message = document.querySelector("#message")

    let base_entrynode = document.querySelector("#entry-base");
    base_entrynode.style.display = "none"

    const agrofood_option = document.querySelector("#agrofoodtype-option");
    let entryid = 0;
    let entrycount = 0;
    let submitbtn = document.querySelector("#submitbtn");

    // ########## FUNCTIONS ##########
    function addentry() {
        // add entry
        let next_entrynode = base_entrynode.cloneNode(true);
        entryid += 1;
        entrycount += 1;
        submitbtn.style.display = "";
        base_entrynode.parentNode.insertBefore(next_entrynode, base_entrynode);        
        next_entrynode.classList.add("entryform");
        next_entrynode.style.display = "";
        // close
        next_entrynode.querySelector("#close-entry").onclick = () => {
            next_entrynode.remove();
            entrycount -= 1;
            submitbtn.style.display = entrycount > 0 ? "" : "none";
        };
        // variables
        let warehouse_pk = next_entrynode.querySelector("#warehouse-pk");
        let agrofood_pk =  next_entrynode.querySelector("#agrofoodtype-pk");
        let gross_weight = next_entrynode.querySelector("#grossweight");
        let packaging_pk = next_entrynode.querySelector("#packaging-pk");
        let num_packages = next_entrynode.querySelector("#num-packages");
        // attribute changes
        //next_entrynode.querySelector("h4").innerHTML = `Entrada ${entryid}`;
        warehouse_pk.name = `entries.${entryid}.warehouse-pk`;
        agrofood_pk.name = `entries.${entryid}.agrofoodtype-pk`;
        gross_weight.name = `entries.${entryid}.grossweight`;
        gross_weight.setAttribute("required", "");
        packaging_pk.name = `entries.${entryid}.packaging-pk`;
        num_packages.name = `entries.${entryid}.numpackages`;
        num_packages.setAttribute("required", "");
        //functions
        function update_disables(){
            if (agrofood_pk.value !== ""){
                gross_weight.removeAttribute("disabled");
            }else{
                gross_weight.setAttribute("disabled", "");
            }
            if (packaging_pk.value !== ""){
                num_packages.removeAttribute("disabled");
            }else{
                num_packages.setAttribute("disabled", "");
            }
        }
        // change title
        // add event listener on add pallet
        let pallet_labels = next_entrynode.querySelector("#pallet-labels");
        let pallet_input_row = next_entrynode.querySelector("#pallet-input-row");
        let palletid = 0;
        let palletcount = 0;
        next_entrynode.querySelector("#add-pallet-btn").onclick = () => {
            pallet_labels.style.display = "";
            let input_row = pallet_input_row.cloneNode(true);
            palletid += 1;
            palletcount += 1;
            let pallet_pk = input_row.querySelector("#pallet-pk");
            pallet_pk.name = `entries.${entryid}.pallets.${palletid}.pallet-pk`;
            pallet_pk.setAttribute("required", "");
            let numpallets = input_row.querySelector("#numpallets");
            numpallets.name = `entries.${entryid}.pallets.${palletid}.numpallets`;
            numpallets.setAttribute("required", "");
            input_row.style.display = "";
            pallet_input_row.parentElement.append(input_row);
            input_row.querySelector("#close-pallet").onclick = () => {
                input_row.remove();
                palletcount -= 1;
                pallet_labels.style.display = palletcount > 0 ? "" : "none";
            };
        };
        // add event listener on warehouse to add agrofoodtypes to selecteor
        warehouse_pk.oninput = () => {
            agrofood_pk.innerHTML = "";
            packaging_pk.value = ""; 
            new_agrofood = agrofood_option.cloneNode(true);
            agrofood_pk.append(new_agrofood);
            fetch(`/api/warehouses/${warehouse_pk.value}`)
            .then(response => response.json())
            .then(data => {
                data.agrofoodtypes.forEach(afood => {
                    new_agrofood = agrofood_option.cloneNode(true);
                    new_agrofood.removeAttribute("hidden");
                    new_agrofood.removeAttribute("selected");
                    new_agrofood.innerHTML = afood.name
                    new_agrofood.value = afood.pk
                    agrofood_pk.append(new_agrofood);
                });
                update_disables();
            })
            .catch(error => {console.log(error)});
        };
        // add event listener on agrofoodtype
        agrofood_pk.oninput = () => {
            fetch(`/api/agrofoodtypes/${agrofood_pk.value}`)
            .then(response => response.json())
            .then(data => {
                packaging_pk.value = data.packaging && data.packaging.pk ? data.packaging.pk  : "";
                update_disables();
            })
            .catch(error => {console.log(error)});
        };
        packaging_pk.oninput = update_disables;
   }


    // ########## EVENT LISTENERS ##########
    document.querySelector("#add-entry").onclick = addentry;

    supplier_pk.oninput = () => {
        if (message) {message.remove()}
        entryid = 0;
        document.querySelectorAll(".entryform").forEach((element) => {
            element.remove();
        })
        // display on/off
        if (supplier_pk.value === ""){
            formdiv.style.display = "none";
        }else{
            //  consulta de datos de agricultor
            fetch(`/api/suppliers/${supplier_pk.value}`)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                supplierdata = data;
                // actualizar transportista y precio porte si estuviera
                carrier_pk.value = supplierdata.carrier ? supplierdata.carrier.pk : "";
                carrier_price.value = supplierdata.carrier && supplierdata.carrier.carrier_price ? parseFloat(supplierdata.carrier.carrier_price) : "";
                carrier_pk.oninput = () => {
                    carrier_price.value = "";
                    if (carrier_pk.value){
                        fetch(`/api/carriers/${carrier_pk.value}`)
                        .then(response => response.json())
                        .then(data => {
                            carrier_price.value = data.carrier_price ? parseFloat(data.carrier_price) : "";
                        })
                        .catch(error => {console.log(error)});
                    }
                }
                // change warehouses input on each entry
                let warehouse = document.querySelector("#warehouse-pk");
                warehouse.querySelectorAll(".next-warehouse").forEach(warehouse => {warehouse.remove()});
                let warehouse_option = document.querySelector("#warehouse-hidden-option");
                supplierdata.land_set.forEach(land => {
                    land.warehouse_set.forEach(ele=> {
                        let next_warehouse = warehouse_option.cloneNode(true);
                        next_warehouse.removeAttribute("hidden");
                        next_warehouse.removeAttribute("selected");
                        next_warehouse.innerHTML = ele.name;
                        next_warehouse.value = ele.pk;
                        next_warehouse.classList.add("next-warehouse");
                        warehouse_option.parentElement.append(next_warehouse);
                    });
                });
            })
            .catch(error => {
                console.log(error);
            });
            // display
            formdiv.style.display = "";
        }
    };
});

