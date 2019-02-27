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
     newSku: { 'sku_name': '','productline': '', 'id': 0, 'caseupc': 100000000000,'unitupc': 100000000000, 'unit_size': 0, 'count': 0, 'formula':0,
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
      // [['ml_short_name': ml_short_name, 'ml_name': ml_name, 'comment': comment, 'all_active': bool, 'part_active': bool] x num_ml]
      ml_status: [],
      case_upc_errors: '',
     unit_upc_errors: '',
     error: '',
   },
   mounted: function() {
       this.getSkus();
       $("#search_input").autocomplete({
        minLength: 1,
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
        minLength: 1,
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
                  // user selection status
                  this.skus = response.data.map((sku) => {
                    // make 'active' property reactive 
                    // https://vuejs.org/v2/guide/reactivity.html#Change-Detection-Caveats
                    Vue.set(sku, 'active', false);
                    return sku;
                  });
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
      viewIngr: function(skuid){
        window.location.href = '/get_sku/'+skuid
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
         if(!this.upcCheck(this.newSku.caseupc)){
          this.case_upc_errors = "case upc not up to format, make sure leading number or check digit is correct";
          return;
         }
         if(!this.upcCheck(this.newSku.unitupc)){
          this.unit_upc_errors = "unit upc not up to format, make sure leading number or check digit is correct";
          return;
         }
         this.$http.post('/api/sku/',this.newSku)
           .then((response) => {
         $("#addSkuModal").modal('hide');
         this.case_upc_errors = "";
         this.loading = false;
         if((this.skus.length%this.perPage)==0){
            this.addPage();
         }
         this.getSkus();
         })
           .catch((err) => {
         this.loading = false;
         this.error = err.bodyText;
         console.log(err);
       })
       },
       updateSku: function() {
         this.loading = true;
         if(!this.upcCheck(this.currentSku.caseupc)){
          this.case_upc_errors = "case upc not up to format, make sure leading number or check digit is correct";
          return;
         }
         if(!this.upcCheck(this.currentSku.unitupc)){
          this.unit_upc_errors = "unit upc not up to format, make sure leading number or check digit is correct";
          return;
         }
         console.log(this.currentSku.id)
         this.$http.put('/api/sku/'+ this.currentSku.id + '/',     this.currentSku)
           .then((response) => {
             $("#editSkuModal").modal('hide');
         this.loading = false;
         this.currentSku = response.data;
         this.getSkus();
         })
           .catch((err) => {
         this.loading = false;
         this.error = err.bodyText;
         console.log(err);
       })
   },
      upcCheck: function(upcnum) {
        if(upcnum.length != 12){
          return false;
        }
        if(upcnum.charAt(0)==="2" || upcnum.charAt(0) === "3" || upcnum.charAt(0) === "4" || upcnum.charAt(0) ==="5"){
          return false;
        } 
        let odds = parseInt(upcnum.charAt(0)) + parseInt(upcnum.charAt(2)) + parseInt(upcnum.charAt(4)) + parseInt(upcnum.charAt(6))
        + parseInt(upcnum.charAt(8))+ parseInt(upcnum.charAt(10));
        odds = odds*3;
        let evens = parseInt(upcnum.charAt(1)) + parseInt(upcnum.charAt(3)) + parseInt(upcnum.charAt(5)) + parseInt(upcnum.charAt(7))
        + parseInt(upcnum.charAt(9));
        let sum = odds + evens;
        if(sum % 10 === 0 && upcnum.charAt(11) != 0){
          return false;
        } else{
          let check = 10 - (sum % 10);
          if(upcnum.charAt(11) != check){
            return false;
          }
        }
        return true;
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

      // store manufacture lines states based on active SKUs
      getManufactureLines: function(event) {
        // Pass the set of active SKUs to API and obtain manufacturing lines status
        let active_skus = this.skus.filter((sku) => {
          return sku.active;
        }).map((sku) => {
          return sku.id
        })
        this.$http.post('/api/active_manufacturing_lines/', active_skus)
        .then((response) => {
            this.ml_status = response.data;
        })
        .catch((err) => {
            console.log(err);
        })
      },

      updateManufactureLines: function(event) {
        let active_skus = this.skus.filter((sku) => {
          return sku.active;
        }).map((sku) => {
          return sku.id;
        })
        let active_mls = this.ml_status.filter((ml) => {
          return ml['all_active'];
        }).map((ml) => {
          return ml['ml_short_name'];
        })
        let request = {
          'active_sku_ids': active_skus,
          'active_ml_short_names': active_mls
        }
        this.$http.post('/api/bulk_match_manufacturing_lines/', request)
        .then((response) => {
          $("#updateMLModal").modal('hide');
        })
        .catch((err) => {
            console.log(err);
        })
      },
   
      ml_checkbox_click: function(ev, ml) {
        ml['part_active'] = false;
      }

   },

  computed: {
    displayedSkus () {
      return this.paginate(this.skus);
    }
  },

   });