This project's aim is to add text layer to your pdf of djvu file.

It works in docker and use rest api.

```bash
docker build -t korrectur . 
docker run --rm -ti -p 1213:1213 korrectur  
```

Now open your browser, choose your file and click the Upload button.

It will return pdf with text layer, default language is english+russian.