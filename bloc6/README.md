<img src='musegen.png'>

This project was made by Iandro, Matrickx, Alexande & Kevin.

This is a team project application which generate random music with a tuned variational autoencoder model.
We used MAGENTA library (https://github.com/magenta/magenta) to create the app.

If you want to try it:

```shell
docker build . -t musegen
```

```shell
docker run -it -v "$(pwd):/home/app" -e PORT=80 -p 4000:80 musegen
```

> Video link to understand the code (FR) : https://share.vidyard.com/watch/RwPJHQhTZHfAUhp2epyv3S?

> Link to download the soundfont museScore_Sf2 :  https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf2

> Link to the app demo : https://share.vidyard.com/watch/bsEUg8R77JVVEGGCbbv52v?
