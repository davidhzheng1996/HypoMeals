var vm = new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     ingredients: [],
     loading: false,
     message: null,
     error:'',
   },
   mounted: function() {
       // this.getGoals();
   },
   methods: {
       getIngredients: function(goalid){
            let api_url = '/api/calculate_goal/'+goalid;
           // if(this.search_term !== '' || this.search_term !== null) {
           //      api_url = '/api/search_manufacture_goal/'+userid+'/'+goalid+this.search_term
           // }
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                   this.ingredients = response.data;
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   this.error = err.bodyText;
                   console.log(err);
               })
       },
       exportCSV: function(){
        this.loading = true;
        // Export all current skus to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent+=[["Ingredient Name", "Unit Quantity", "Package Quantity"].join(",")+'\n'];
        for(key in this.ingredients){
          csvContent+=[[key, this.ingredients[key]].join(",")+'\n'];
        }
        const url = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "calculatedIngredients.csv");
        link.click();
       },
      
      exportPDF: function(){
        // let pdfName = 'test'; 
        // var doc = new jsPDF();
        // doc.text("Ingredient Name, Quantity", 10, 10);
        // for(key in this.ingredients){
        //   doc.text("key, this.ingredients[key]", 10, 10);
        // }
        // doc.save(pdfName + '.pdf');
        const doc = new jsPDF();
        doc.autoTable({html: '#my-table'});
        doc.save('calculatedIngredients.pdf');
      },
   },
   });