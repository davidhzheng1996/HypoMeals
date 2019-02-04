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
     perPage: 2,
     pages:[],
     newSku: { 'sku_name': '','productline': '', 'id': null, 'caseupc': 1234,'unitupc': 1234, 'unit_size': 0, 'count': 0, 'tuples': null, 
     'comment': null},
     skuFile: null,
     search_term: '',
     has_paginated:false,
     csv_uploaded:false,

     search_term: '',
     search_suggestions: search_suggestions,
     search_input: '',

     suggestionAttribute: 'original_title',

     sortKey: 'sku_name',
     sortAsc: [
            { 'sku_name': true },
            { 'id': true },
            { 'productline': true },
            { 'caseupc': true },
            {'unitupc': true},
            {'unit_size': true},
            {'count': true},
          ],
   },
   mounted: function() {
       this.getSkus();
   },
   methods: {
       getSkus: function(){
          let api_url = '/api/isku/';
           // https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
           if(this.search_term !== '' || this.search_term !== null) {
                api_url = '/api/sku/?search=' + this.search_term;
           }
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                   this.skus = response.data;
                   this.loading = false;
                   this.lowerCaseName();
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
         for(let index = 0; index<this.skus.length; index++){
            if(this.newSku.sku_name.toLowerCase().trim()===(this.skus[index].sku_name.toLowerCase().trim())){
                console.log("Already exists");
                return;
                //console.log(err);
            }
          }
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
       lowerCaseName: function(){
          for(let index = 0; index<this.skus.length; index++){
            this.skus[index].sku_name = this.skus[index].sku_name.toLowerCase().trim();
          }
       },
       updateSku: function() {
         this.loading = true;
         console.log(this.currentSku)
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
         this.loading = false;
         this.csv_uploaded=true;
         this.getSkus();
         })
           .catch((err) => {
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

      search_input_changed: function() {
        const that = this
        this.$http.get('/api/sku/?search=' + this.search_term)
                .then((response) => {
                        for (var i in response.data) {
                                this.search_suggestions.push(response.data[i].sku_name.toLowerCase());
                        }
                })
      },

        sortBy: function(key) {
        this.sortKey = key
        this.sortAsc[key] = !this.sortAsc[key]
        if(!this.sortAsc[this.sortKey]){
          this.skus = _.sortBy(this.skus, this.sortKey)
        } else {
          this.iskus = _.sortBy(this.skus, this.sortKey).reverse()
        }
      },
   
   
   },


  computed: {
    displayedSkus () {
      return this.paginate(this.skus);
    }
  },

   });