new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     skus: [],
     loading: false,
     query:'',
     currentSku: {},
     message: null,
     newSku: { 'sku_name': '','productline': '', 'id': null, 'caseupc': 1234,'unitupc': 1234, 'unit_size': 0, 'count': 0, 'tuple': null, 
     'comment': null},
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
   }
   
   
   }
   });