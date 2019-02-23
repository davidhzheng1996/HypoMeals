new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     manufacture_lines: [],
     loading: false,
     currentManufactureLine: {},
     message: null,
     newManufactureLine: { 'ml_name': '', 'ml_short_name': '', 'comment' :null,},
     message: '',
     page:1,
     perPage: 10,
     pages:[],
     has_paginated:false,
     upload_errors: '',
     short_name_errors: '',
   },
   mounted: function() {
       this.getManufactureLines();
   },
   methods: {
       getManufactureLines: function(){
           let api_url = '/api/manufacture_line/';
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                   this.manufacture_lines = response.data;
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
       getManufactureLine: function(name){
           this.loading = true;
           this.$http.get('/api/manufacture_line/'+name+'/')
               .then((response) => {
                   this.currentManufactureLine = response.data;
                   $("#editManufactureLineModal").modal('show');
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       deleteManufactureLine: function(name){
         this.loading = true;
         // TODO: use delimiters
         this.$http.delete('/api/manufacture_line/' + name + '/')
           .then((response) => {
             this.loading = false;
             if((this.manufacture_lines.length%this.perPage)==1){
                      this.deletePage();
                    }
             this.getManufactureLines();
           })
           .catch((err) => {
             this.loading = false;
             this.message = err.data
             console.log(err);
           })
       },
       addManufactureLine: function() {
         this.loading = true;
         if(this.newManufactureLine.ml_short_name.indexOf(' ') >= 0 || this.newManufactureLine.ml_short_name.length > 5){
            this.short_name_errors = "short name invalid"
         }
         this.$http.post('/api/manufacture_line/',this.newManufactureLine)
           .then((response) => {
         $("#addManufactureLineModal").modal('hide');
         this.loading = false;
         if((this.manufacture_lines.length%this.perPage)==0){
            this.addPage();
         }
         this.getManufactureLines();
         })
           .catch((err) => {
         this.loading = false;
         this.message = err.data;
         console.log(err.bodyText);
       })
       },
       setPages: function () {
        let numberOfPages = Math.ceil(this.manufacture_lines.length / this.perPage);
        for (let index = 1; index <= numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      addPage: function (){
          this.pages.push(Math.ceil(this.manufacture_lines.length / this.perPage)+1);
      },
      deletePage: function (){
        this.pages=[];
          let numberOfPages = Math.ceil(this.manufacture_lines.length / this.perPage);
        for (let index = 1; index < numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      paginate: function (manufacture_lines) {
      let page = this.page;
      // console.log(page)
      let perPage = this.perPage;
      let from = (page * perPage) - perPage;
      let to = (page * perPage);
      return  manufacture_lines.slice(from, to);
    },
        
       updateManufactureLine: function() {
         this.loading = true;
         this.$http.put('/api/manufacture_line/'+ this.currentManufactureLine.manufacture_line_name + '/',     this.currentManufactureLine)
           .then((response) => {
             $("#editManufactureLineModal").modal('hide');
         this.loading = false;
         this.currentManufactureLine = response.data;
         this.csv_uploaded=true;
         this.getManufactureLines();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
        })
      },
   },

   computed: {
    displayedManufactureLines () {
      return this.paginate(this.manufacture_lines);
    }
  },
   });