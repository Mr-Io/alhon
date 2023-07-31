const number_options = { 
  minimumFractionDigits: 2,
  maximumFractionDigits: 2 
};
document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let table = new DataTable('#packaging-table', {
        paging: false,
        fixedHeader: true,
    });
});

