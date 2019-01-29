new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     product_lines: [],
     loading: false,
     currentProductLine: {},
     message: null,
     newProductLine: { 'product_line_name': '',},
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
             console.log(err);
           })
       },
       addProductLine: function() {
         this.loading = true;
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
       updateProductLine: function() {
         this.loading = true;
         console.log(this.currentProductLine)
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