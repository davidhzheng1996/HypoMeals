new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     skus: [],
     loading: false,
     query:'',
     currentSku: {},
     message: null,
     newSku: { 'sku_name': '','productline': '', 'id': null, 'caseupc': 1234,'unitupc': 1234, 'unit_size': 0, 'count': 0, 'tuples': null, 
     'comment': null},
     skuFile: null,
     search_term: ''
   },
   mounted: function() {
       this.getSkus();
   },
   methods: {
       getSkus: function(){
           this.loading = true;
           this.$http.get('/api/sku/')
               .then((response) => {
                   this.skus = response.data;
                   this.loading = false;
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
             this.getSkus();
           })
           .catch((err) => {
             this.loading = false;
             console.log(err);
           })
       },
       addSku: function() {
         this.loading = true;
         this.$http.post('/api/sku/',this.newSku)
           .then((response) => {
         $("#addSkuModal").modal('hide');
         this.loading = false;
         this.getSkus();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
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
         this.getSkus();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
        })
      },

      exportSkuCSV: function() {
        this.loading = true;
        this.$http.get('/api/sku_export/')
          .then((response) => {
                // https://thewebtier.com/snippets/download-files-with-axios/
                // https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL
                // url to the csv file in form of a Blob
                // url lifetime is tied to the document in the window
                const url = window.URL.createObjectURL(new Blob([response.data]));
                // create a link with the file url and click on it
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', 'sku.csv');
                document.body.appendChild(link);
                link.click();
                
                this.loading = false;
                this.getSkus();
          }).catch((err) => {
                this.loading = false;
                console.log(err)
          })
      },
   
   
   }
   });