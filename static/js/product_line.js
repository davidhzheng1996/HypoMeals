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
     page:1,
     perPage: 10,
     pages:[],
     has_paginated:false,
     csv_uploaded:false,
     productlineFile: null,
     upload_errors: ''
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
                   if(!this.has_paginated){
                      this.setPages();
                      this.has_paginated=true; 
                    }
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
             if((this.product_lines.length%this.perPage)==1){
                      this.deletePage();
                    }
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
         if((this.product_lines.length%this.perPage)==0){
            this.addPage();
         }
         this.getProductLines();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       setPages: function () {
        let numberOfPages = Math.ceil(this.product_lines.length / this.perPage);
        for (let index = 1; index <= numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      addPage: function (){
          this.pages.push(Math.ceil(this.product_lines.length / this.perPage)+1);
      },
      deletePage: function (){
        this.pages=[];
          let numberOfPages = Math.ceil(this.product_lines.length / this.perPage);
        for (let index = 1; index < numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      paginate: function (product_lines) {
      let page = this.page;
      // console.log(page)
      let perPage = this.perPage;
      let from = (page * perPage) - perPage;
      let to = (page * perPage);
      return  product_lines.slice(from, to);
    },
       selectCSV: function(event) {
        this.productlineFile = event.target.files[0]
      },
        
      uploadCSV: function() {
        this.loading = true;
        // upload this.ingredientCSV to REST api in FormData
        const formData = new FormData()
        // https://developer.mozilla.org/en-US/docs/Web/API/FormData/append
        formData.append('file', this.productlineFile, this.productlineFile.name)
        this.$http.post('/api/product_line_import/', formData)
           .then((response) => {
            this.upload_errors = response.data['errors'].join('\n') + response.data['warnings'].join('\n')
         this.loading = false;
         this.csv_uploaded=true;
         this.getProductLines();
         })
           .catch((err) => {
             console.log(err)
            this.upload_errors = err.data['errors'].join('\n') + err.data['warnings'].join('\n')
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
   },

   computed: {
    displayedProductLines () {
      return this.paginate(this.product_lines);
    }
  },
   });