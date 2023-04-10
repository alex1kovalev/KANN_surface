# KANN_surface
Kohonen SOM using ANN to evaluate the clustering for amplitude roughness parameters of surface.
This project is based on the original implementation of the Kohonen SOM for Tensorflow and Python proposed by [Chris Gorman](https://github.com/cgorman) and [Dragan Avramovski](https://github.com/dragan-avramovski) .

**The main objective** of the project is to try to identify and locate areas with similar roughness parameters on a real rough surface by means of an unsupervised learning algorithm (Kohonen self-organised map) improved by the neural network technique.
To do this, the original images (eight AFM images are located in a folder '.\AFM surf_data\') of the friction track were used to generate a roughness clustering map. The amplitude roughness parameters such as Sa, Sq, Ssk, Sku were used as input features for the Kohanen meural network (KANN).

## Routine flow
an example of real rough surface to investigate
 ![rough surface](https://github.com/alex1kovalev/KANN_surface/blob/main/Output%20Data/Rought%20surface.png)

 * The surface is divided into 19 square subsurfaces (can be manually changed to any other set).
 * The set of roughness parameters is calculated for each subsurfaces. These feature sets are used to train the KANN. The resulting U-Matrix shuold look like this: ![U-Matrix](https://github.com/alex1kovalev/KANN_surface/blob/main/Output%20Data/U_matrix%20for%20subimages.png)
 * Every feature has a weight map representing its clustering.![Sa weight matrix](https://github.com/alex1kovalev/KANN_surface/blob/main/Output%20Data/Sa%20weight%20matrix.png) 

* Overlaying the coloured images of the subsurface and a particular weight map allows the subsurface map to be highlighted.![Sa & subsurfaces](https://github.com/alex1kovalev/KANN_surface/blob/main/Output%20Data/U_matrix%2for%20Sa%20of%20subimages.png)
* the backward is carried out to identify the original location of each surface highlighted by a given roughness mask.![Surface & mask](https://github.com/alex1kovalev/KANN_surface/blob/main/Output%20Data/Rough%20surface%20with%20a%20colored%20mask%20of%20Sa.png)