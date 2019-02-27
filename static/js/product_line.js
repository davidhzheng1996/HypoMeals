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
     csv_data:'',
     productlineFile: null,
     upload_errors: '',
     name_error:'',
     error:'',

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
                    if(this.csv_uploaded){
                      this.pages=[];
                      this.setPages();
                      this.csv_uploaded=false;
                    }
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       getProductLine: function(name){
           this.loading = true;
           this.$http.get('/api/product_line/'+name+'/')
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
       deleteProductLine: function(name){
         this.loading = true;
         // TODO: use delimiters
         this.$http.delete('/api/product_line/' + name + '/')
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
         for (let index = 0; index < this.product_lines.length; index++) {
            if (this.newProductLine.product_line_name.toLowerCase() === this.product_lines[index].product_line_name.toLowerCase()) {
              this.name_error = "name exists"
              return;
            }
          }
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
        console.log(this.productlineFile)
      },
        
      uploadCSV: function() {
        this.loading = true;

        var reader = new FileReader();
        reader.readAsText(this.productlineFile)
        reader.onload = (event)=> {
                this.csvData = event.target.result;
                $.post('/api/product_line_import/', {'data':this.csvData}, (response)=>{
                     this.loading = false;
                     this.csv_uploaded=true;
                     this.getProductLines();
                 });
                // console.log(this.csvData)
                // data = $.csv.toArrays(csvData);
                // if (data && data.length > 0) {
                //   alert('Imported -' + data.length + '- rows successfully!');
                // } else {
                //     alert('No data to import!');
                // }
        };
        reader.onerror = function() {
            alert('Unable to read ' + file.fileName);
        };
        // upload this.ingredientCSV to REST api in FormData
        // console.log(this.csvData)
        // console.log(typeof this.csvData)
        // const formData = new FormData()
        // // https://developer.mozilla.org/en-US/docs/Web/API/FormData/append
        // console.log(this.productlineFile)
        // formData.append('file', this.productlineFile, this.productlineFile.name)
        
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
         this.$http.put('/api/product_line/'+ this.currentProductLine.product_line_name + '/',     this.currentProductLine)
           .then((response) => {
             $("#editProductLineModal").modal('hide');
         this.loading = false;
         this.currentProductLine = response.data;
         this.csv_uploaded=true;
         this.getProductLines();
         })
           .catch((err) => {
         this.loading = false;
         this.error = err.bodyText;
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