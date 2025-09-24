'use strict';
{
  window.addEventListener('load', () => {
    // If the 'Export emails' button is clicked...
    document.querySelector('.export-emails').addEventListener('click', (event) => {
      event.preventDefault();

      // If present, get the 'groups__id__exact' value from the URL.
      const params = new URLSearchParams(window.location.search);
      let groupID = '';
      if (params.has('groups__id__exact')) {
        groupID = params.get('groups__id__exact');
      }

      // Fetch the relevant user email addresses and display them in an alert.
      fetch('/accounts/export-emails/' + groupID)
        .then(response => {
          if (response.ok) {
            return response.json();
          }
          else {
            throw new Error(`Response status: ${response.status}`);
          }
        })
        .then(data => {
          let emails = '';
          for (const key in data) {
            emails += "<" + data[key] + ">;";
          }
          alert(emails);
        });
    });
  });
}
