new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     product_lines: [],
     loading: false,
     currentProductLine: {},
     message: null,
     newProductLine: { 'product_line_name': '',},
     message: '',
   },
   mounted: function() {
       this.getProductLines();
   },
   methods: {
       getProductLines: function(){
           let api_url = '/api/product_line/';
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                   this.product_lines = response.data;
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       getProductLine: function(id){
           this.loading = true;
           this.$http.get('/api/product_line/'+id+'/')
               .then((response) => {
                   this.currentProductLine = response.data;
                   $("#editProductLineModal").modal('show');
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       deleteProductLine: function(id){
         this.loading = true;
         // TODO: use delimiters
         this.$http.delete('/api/product_line/' + id + '/')
           .then((response) => {
             this.loading = false;
             this.getProductLines();
           })
           .catch((err) => {
             this.loading = false;
             this.message = err.data
             console.log(err);
           })
       },
       addProductLine: function() {
         this.loading = true;
         this.newProductLine.product_line_name = this.newProductLine.product_line_name.toLowerCase();
         this.$http.post('/api/product_line/',this.newProductLine)
           .then((response) => {
         $("#addProductLineModal").modal('hide');
         this.loading = false;
         this.getProductLines();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       exportCSV: function(){
        this.loading = true;
        // Export all current skus to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent += [
          Object.keys(this.product_lines[0]).join(","),
          // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
          ...this.product_lines.map(key => Object.values(key).join(","))
        ].join("\n");
        const url = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "product_line.csv");
        link.click();
       },
       updateProductLine: function() {
         this.loading = true;
        this.currentProductLine.product_line_name = this.currentProductLine.product_line_name.toLowerCase();
         this.$http.put('/api/product_line/'+ this.currentProductLine.id + '/',     this.currentProductLine)
           .then((response) => {
             $("#editProductLineModal").modal('hide');
         this.loading = false;
         this.currentProductLine = response.data;
         this.getProductLines();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
        })
      },
   }
   });