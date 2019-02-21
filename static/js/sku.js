Vue.filter('lowercase', function (value) {
   return value.toLowerCase()
})
new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     skus: [],
     loading: false,
     query:'',
     currentSku: {},
     message: null,
     page:1,
     perPage: 10,
     pages:[],
     newSku: { 'sku_name': '','productline': '', 'id': null, 'caseupc': 1234,'unitupc': 1234, 'unit_size': 0, 'count': 0, 'formula':0,
     'formula_scale_factor':0, 'manufacture_rate':0,'comment': null},
     skuFile: null,
     formulaFile: null,
     has_paginated:false,
     csv_uploaded:false,
     search_term: '',
     search_input: '',
     sortKey: 'sku_name',
     sortAsc: [
            { 'sku_name': true },
            { 'id': true },
            { 'productline': true },
            { 'caseupc': true },
            {'unitupc': true},
            {'unit_size': true},
            {'count': true},
            {'formula': true},
            {'formula_scale_factor': true},
            {'manufacture_rate': true},
          ],
      upload_errors: '',
   },
   mounted: function() {
       this.getSkus();
       $("#search_input").autocomplete({
        minLength: 2,
        delay: 100,
        // https://stackoverflow.com/questions/9656523/jquery-autocomplete-with-callback-ajax-json
        source: function (request, response) {
          $.ajax({
            url: "/api/sku",
            dataType: "json",
            data: {
              // attach '?search=request.term' to the url 
              search: request.term
            },
            success: function (data) {
              names = $.map(data, function (item) {
                return [item.sku_name];
              })
              response(names);
            }
          });
        },
        messages: {
          noResults: '',
          results: function() {}
        }
      });
      $("#product_line_search_input").autocomplete({
        minLength: 2,
        delay: 100,
        // https://stackoverflow.com/questions/9656523/jquery-autocomplete-with-callback-ajax-json
        source: function (request, response) {
          $.ajax({
            url: "/api/product_line",
            dataType: "json",
            data: {
              // attach '?search=request.term' to the url 
              search: request.term
            },
            success: function (data) {
              names = $.map(data, function (item) {
                return [item.product_line_name];
              })
              response(names);
            }
          });
        },
        appendTo: "#addSkuModal",
        messages: {
          noResults: '',
          results: function() {}
        }
      });
   },
   methods: {
       getSkus: function(){
          let api_url = '/api/sku/';
           // https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
           if(this.search_term !== '' && this.search_term !== null) {
                api_url = '/api/sku/?search=' + this.search_term;
           }
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                   this.skus = response.data;
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
       getSku: function(id){
           this.loading = true;
           this.$http.get('/api/sku/'+id+'/')
               .then((response) => {
                   this.currentSku = response.data;
                   $("#editSkuModal").modal('show');
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       deleteSku: function(id){
         this.loading = true;
         // TODO: use delimiters
         this.$http.delete('/api/sku/' + id + '/')
           .then((response) => {
             this.loading = false;
                    if((this.skus.length%this.perPage)==1){
                      this.deletePage();
                    }
             this.getSkus();
           })
           .catch((err) => {
             this.loading = false;
             console.log(err);
           })
       },
      setPages: function () {
        let numberOfPages = Math.ceil(this.skus.length / this.perPage);
        for (let index = 1; index <= numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      viewFormula: function(formulaid){
        window.location.href = '/sku/'+formulaid
      },
      addPage: function (){
          this.pages.push(Math.ceil(this.skus.length / this.perPage)+1);
      },
      deletePage: function (){
        this.pages=[];
          let numberOfPages = Math.ceil(this.skus.length / this.perPage);
        for (let index = 1; index < numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      paginate: function (skus) {
      let page = this.page;
      let perPage = this.perPage;
      let from = (page * perPage) - perPage;
      let to = (page * perPage);
      return  skus.slice(from, to);
    },
       addSku: function() {
         this.loading = true;
         this.$http.post('/api/sku/',this.newSku)
           .then((response) => {
         $("#addSkuModal").modal('hide');
         this.loading = false;
         // for(let index = 0; index<this.skus.length; index++){
         //    if(this.newSku.sku_name.toLowerCase()===this.skus[index].sku_name.toLowerCase()){
         //        console.log("Already exists");
         //        return;
         //    }
         //  }
         if((this.skus.length%this.perPage)==0){
            this.addPage();
         }
         this.getSkus();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       updateSku: function() {
         this.loading = true;
         this.$http.put('/api/sku/'+ this.currentSku.id + '/',     this.currentSku)
           .then((response) => {
             $("#editSkuModal").modal('hide');
         this.loading = false;
         this.currentSku = response.data;
         this.getSkus();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
   },

      selectSkuCSV: function(event) {
        this.skuFile = event.target.files[0]
      },
        
      uploadSkuCSV: function() {
        this.loading = true;
        // upload this.ingredientCSV to REST api in FormData
        const formData = new FormData()
        // https://developer.mozilla.org/en-US/docs/Web/API/FormData/append
        formData.append('file', this.skuFile, this.skuFile.name)
        this.$http.post('/api/sku_import/', formData)
           .then((response) => {
            this.upload_errors = response.data['errors'].join('\n') + response.data['warnings'].join('\n')
            console.log(this.upload_errors)
         this.loading = false;
         this.csv_uploaded=true;
         this.getSkus();
         })
           .catch((err) => {
            this.upload_errors = err.data['errors'].join('\n') + err.data['warnings'].join('\n')
         this.loading = false;
         console.log(err);
        })
      },

      selectFormulaCSV: function(event) {
        this.formulaFile = event.target.files[0]
      },
        
      uploadFormulaCSV: function() {
        this.loading = true;
        // upload this.ingredientCSV to REST api in FormData
        const formData = new FormData()
        // https://developer.mozilla.org/en-US/docs/Web/API/FormData/append
        formData.append('file', this.formulaFile, this.formulaFile.name)
        this.$http.post('/api/sku_formula_import/', formData)
           .then((response) => {
            this.upload_errors = response.data['errors'].join('\n') + response.data['warnings'].join('\n')
            console.log(this.upload_errors)
         this.loading = false;
         this.csv_uploaded=true;
         this.getSkus();
         })
           .catch((err) => {
            this.upload_errors = err.data['errors'].join('\n') + err.data['warnings'].join('\n')
         this.loading = false;
         console.log(err);
        })
      },

      exportSkuCSV: function() {
        this.loading = true;
        // Export all current skus to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent += [
          Object.keys(this.skus[0]).join(","),
          // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
          ...this.skus.map(key => Object.values(key).join(","))
        ].join("\n");
        const url = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "sku.csv");
        link.click();
        // this.loading = true;
        // this.$http.get('/api/sku_export/')
        //   .then((response) => {
        //         // https://thewebtier.com/snippets/download-files-with-axios/
        //         // https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL
        //         // url to the csv file in form of a Blob
        //         // url lifetime is tied to the document in the window
        //         const url = window.URL.createObjectURL(new Blob([response.data]));
        //         // create a link with the file url and click on it
        //         const link = document.createElement('a');
        //         link.href = url;
        //         link.setAttribute('download', 'sku.csv');
        //         document.body.appendChild(link);
        //         link.click();
                
        //         this.loading = false;
        //         this.getSkus();
        //   }).catch((err) => {
        //         this.loading = false;
        //         console.log(err)
        //   })
      },

      exportFormula: function(){
        this.loading = true;
        // Export all current ingredients to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        let csvContent = "data:text/csv;charset=utf-8,";

        csvContent+=[["Sku ID", "Ingr ID", "Quantity"].join(",")+'\n'];
        let c = 0
        //console.log(csvContent);
        for (let i = 0; i < this.skus.length; i++) {
                //console.log(this.ingredients[key].ingredient_name)
                this.$http.get('/api/ingredients_to_sku/'+this.skus[i].id)
               .then((response) => {
                  c = c + 1;
                   var ingredients = [];
                   this.ingredients = response.data;
                   for(let j = 0; j < this.ingredients.length; j++){
                        csvContent+=[[this.skus[i].id,this.ingredients[j].id, this.ingredients[j].quantity].join(",")+'\n'];
                      
                   }
                  // this.finished();
                  if(c==this.skus.length){
                     console.log(csvContent);
                   
                     const url = encodeURI(csvContent);
                      const link = document.createElement("a");
                     link.setAttribute("href", url);
                     link.setAttribute("download", "formulas.csv");
                     link.click();
                 }
                   this.loading = false;
                   //this.has_called = true; 
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })

        } 
      

      },

        sortBy: function(key) {
        this.sortKey = key
        this.sortAsc[key] = !this.sortAsc[key]
        if(!this.sortAsc[this.sortKey]){
          this.skus = _.sortBy(this.skus, this.sortKey)
        } else {
          this.skus = _.sortBy(this.skus, this.sortKey).reverse()
        }
      },
      
      onBlur: function(event) {
        if (event && this.search_term !== event.target.value) 
          this.search_term = event.target.value
      },

      onBlurProductLine: function(event) {
        if (event && this.newSku.productline !== event.target.value) 
          this.newSku.productline = event.target.value
      },

   
   },


  computed: {
    displayedSkus () {
      return this.paginate(this.skus);
    }
  },

   });