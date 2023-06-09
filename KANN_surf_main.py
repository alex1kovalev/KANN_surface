# MIT License
#
# Copyright (c) 2018 Chris Gorman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# =================================================================================

"""
Created on Fri Apr  7 10:16:39 2023

@author: Alexander Kovalev
"""

#utils
import numpy as np
import matplotlib.pyplot as plt
import logging
import tensorflow as tf

from tf_som import SelfOrganizingMap
from sklearn.preprocessing import StandardScaler
from scipy.spatial import distance_matrix

from correction_bmu_loc import correction_bmu_location

from surf_param import get_Sa
from surf_param import get_Ssk
from surf_param import get_Sku
from surf_param import get_Sq


#local functions
def load_surf_file_ASCII(input_file_ASCII):
    '''
    local function to load the real surface data from *.asc file 
    (file generated by Gwiddion soft)
    code was written in a rough way), but it works well enough for our purpose)
    '''
    
    file_name = input_file_ASCII
    n_lines = 11 # header
    try:
        file = open(file_name, 'r')
        for i in range (n_lines):
            line = file.readline()
            if i == 3: x_pix = int(line.strip().split('= ')[1])     #pixels in x line
            if i == 4: y_pix = int(line.strip().split('= ')[1])     # pixels in y line
            if i == 5: x_len = float(line.strip().split('= ')[1])   # length in x line
            if i == 6: y_len = float(line.strip().split('= ')[1])   # length in x line
        surf_data = np.genfromtxt(file, delimiter = '\t')
    except Exception as e: print(str(e))
    finally: file.close()
    
    # summarised length/weight data
    params = (x_len, x_pix, y_len, y_pix)
    
    # output is surf_data in Numpy format
    return surf_data, params


# func confert weights to RGB
def weights4_to_RGB(t_weights, m, n):
    #recalculating the wieght data to color RGB data
    
    
    '''
    #transformation for CMYK case - not used in current version
    r = rgb_scale*(1.0-(c+k)/float(cmyk_scale))
    g = rgb_scale*(1.0-(m+k)/float(cmyk_scale))
    b = rgb_scale*(1.0-(y+k)/float(cmyk_scale))
    return r,g,b    

    rgb_scale = 255
    cmyk_scale = 100

    c = t_weights[:, :, 0]
    m = t_weights[:, :, 1]
    y = t_weights[:, :, 2]
    k = t_weights[:, :, 3]
    
    '''
    
    t_weights = t_weights - t_weights.min()
    t_weights = t_weights / t_weights.max() 
    
    c0 = t_weights[:, 0].reshape((m, n))
    m1 = t_weights[:, 1].reshape((m, n))
    y2 = t_weights[:, 2].reshape((m, n))
    k3 = t_weights[:, 3].reshape((m, n))


    weights_RGB = np.zeros(shape=(m,n,3))
    weights_RGB[:, :, 0] = 1 - (c0 * (1.0 - k3) + k3)
    weights_RGB[:, :, 1] = 1 - (m1 * (1.0 - k3) + k3)
    weights_RGB[:, :, 2] = 1 - (y2 * (1.0 - k3) + k3)
    '''
    weights_RGB[:, :, 0] = rgb_scale*(1.0-(c0+k3)/float(cmyk_scale))
    weights_RGB[:, :, 1] = rgb_scale*(1.0-(m1+k3)/float(cmyk_scale))
    weights_RGB[:, :, 2] = rgb_scale*(1.0-(y2+k3)/float(cmyk_scale))
    '''
    
    return weights_RGB
    
    
#-----------------------------------------------------------------------------

def get_umatrix(input_vects, weights, m, n):
    #copied from: https://github.com/cgorman/tensorflow-som/blob/master/example.py
    
    
    """ Generates an n x m u-matrix of the SOM's weights and bmu indices of all the input data points

    Used to visualize higher-dimensional data. Shows the average distance between a SOM unit and its neighbors.
    When displayed, areas of a darker color separated by lighter colors correspond to clusters of units which
    encode similar information.
    :param weights: SOM weight matrix, `ndarray`
    :param m: Rows of neurons
    :param n: Columns of neurons
    :return: m x n u-matrix `ndarray` 
    :return: input_size x 1 bmu indices 'ndarray'
    """
    umatrix = np.zeros((m * n, 1))
    # Get the location of the neurons on the map to figure out their neighbors. I know I already have this in the
    # SOM code but I put it here too to make it easier to follow.
    neuron_locs = list()
    for i in range(m):
        for j in range(n):
            neuron_locs.append(np.array([i, j]))
    # Get the map distance between each neuron (i.e. not the weight distance).
    neuron_distmat = distance_matrix(neuron_locs, neuron_locs)

    for i in range(m * n):
        # Get the indices of the units which neighbor i
        neighbor_idxs = neuron_distmat[i]  <= 1  # Change this to `< 2` if you want to include diagonal neighbors
        # Get the weights of those units
        neighbor_weights = weights[neighbor_idxs]
        # Get the average distance between unit i and all of its neighbors
        # Expand dims to broadcast to each of the neighbors
        umatrix[i] = distance_matrix(np.expand_dims(weights[i], 0), neighbor_weights).mean()

    bmu_indices = []
    bmu_indices_corr = []
    
    for vect in input_vects:
        min_index = min([i for i in range(len(list(weights)))],
                        key=lambda x: np.linalg.norm(vect-
                                                     list(weights)[x]))
        bmu_indices.append(neuron_locs[min_index])
        '''
        lets try to correct...
        '''            
        bmu_indices_corr = correction_bmu_location(bmu_indices)
    return umatrix, bmu_indices_corr  #, bmu_indices
#    return umatrix, bmu_indices



#-----------------------------------------------------------------------------
if __name__ == "__main__":
    
# 8 real surfaces to KANN classification
#    /AFM data/worn area 1.bcrf.gsf.asc'
#    /AFM data/worn area 2.bcrf.gsf.asc'
#    /AFM data/worn area 3.bcrf.gsf.asc'
#    /AFM data/worn area 4.bcrf.gsf.asc'
#    /AFM data/worn area 5.bcrf.gsf.asc'
#    /AFM data/worn area 6.bcrf.gsf.asc'
#    /AFM data/worn area 7.bcrf.gsf.asc'
#    /AFM data/worn area 8.bcrf.gsf.asc'

    file_name = './AFM surf_data/'+'worn area 8.bcrf.gsf.asc'
    
    # directory to save output images
    dir_im = './Output Data/'
    
    s_data, s_params = load_surf_file_ASCII(file_name)
    
    # lets plot it
    # creating 2D array for x and y
    x = np.linspace(0, s_params[0], s_params[1])
    y = np.linspace(0, s_params[2], s_params[3])
    xv, yv = np.meshgrid(x, y) 
    
    fig, ax = plt.subplots()
    
    fig.set_figwidth(fig.get_figwidth()*2)
    fig.set_figheight(fig.get_figheight()*2)
    im = ax.imshow(s_data, interpolation='none', cmap = 'gray', 
#                   vmin = s_data.min(), vmax = s_data.max(),
                   extent=[s_params[1] // 1000, s_params[0] // 1000, s_params[3] // 1000, s_params[2] // 1000], 
                   clip_on=True)
    plt.title('Rough surface to analyse')
    plt.xlabel('Friction distance ($\mu $m)')
    plt.ylabel('Friction width ($\mu $m)')
#    plt.colorbar(im, label='Height (nm)', shrink = 0.2)
    plt.show()
    fig.savefig(dir_im+'Rough surface.png', dpi = 150)
    
#   lets divide a surface to set of subsurfaces 20x20 pxl.
    subsurf_pxl = 15

    sub_surf = list()
    sub_surf_ind = list()
    sub_surf_S_param = list()
#    subsurf_n_x = int( s_params[1] / subsurf_pxl)
#    subsurf_n_y = int( s_params[3] / subsurf_pxl)
    y_ind, x_ind = s_data.shape
    ind = 0
    for i in range(0, y_ind, subsurf_pxl):
        for j in range(0, x_ind, subsurf_pxl): 
            # add sybsyefaces
            if i+subsurf_pxl<=y_ind and j+subsurf_pxl<=x_ind: 
                sub_surf.append(s_data[i:i+subsurf_pxl, j:j+subsurf_pxl].copy())
                sub_surf_ind.append([i, j])
                sub_surf[ind] -= sub_surf[ind].min()
                sub_surf_S_param.append([get_Sa(sub_surf[ind]), get_Sq(sub_surf[ind]), get_Ssk(sub_surf[ind]), get_Sku(sub_surf[ind])])
                ind = ind+1
            
    #main data of surface parameters - sub_surf_S_param(Sa, Sq, Ssk. Sku)
    sub_surf_S_data = np.asarray(sub_surf_S_param)  

    '''
    lets go to Kohanen ANN)))))))))))
    
    ''' 

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    graph = tf.Graph()
    with graph.as_default():
        # Make sure you allow_soft_placement, some ops have to be put on the CPU (e.g. summary operations)
        session = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(
            allow_soft_placement=True,
            log_device_placement=False))

        num_inputs = sub_surf_S_data.shape[0]
        dims = sub_surf_S_data.shape[1]
        # This is more neurons than you need but it makes the visualization look nicer
        m_t, n_t = s_data.shape
        m_t = m_t // subsurf_pxl
        n_t = n_t // subsurf_pxl
        m = int((m_t*n_t)**(0.5))
        n = int((m_t*n_t)**(0.5))

        scaler = StandardScaler()
        input_data = scaler.fit_transform(sub_surf_S_data)
        batch_size = 128  # int((m_t*n_t)**(0.5)) #128 - need to know whT IS IT....
        
        # Build the TensorFlow dataset pipeline per the standard tutorial.
        dataset = tf.data.Dataset.from_tensor_slices(input_data.astype(np.float32))
        dataset = dataset.repeat()
        dataset = dataset.batch(batch_size)
        iterator =  tf.compat.v1.data.make_one_shot_iterator(dataset)
        next_element = iterator.get_next()

        # Build the SOM object and place all of its ops on the graph
        som = SelfOrganizingMap(m=m, n=n, dim=dims, max_epochs=50000, gpus=1,
                                session=session, graph=graph,
                                input_tensor=next_element,
                                batch_size=batch_size, initial_learning_rate=0.1)
        init_op = tf.compat.v1.global_variables_initializer()
        session.run([init_op])
        # Note that I don't pass a SummaryWriter because I don't really want to record summaries in this script
        # If you want Tensorboard support just make a new SummaryWriter and pass it to this method
        tmp_dir = './logs'
        


#        writer = tf.compat.v1.summary.FileWriter(tmp_dir, session.graph)
        
        som.train(num_inputs=num_inputs)#, writer= writer)
        
        weights = som.output_weights
        
        # if need to check the local parameters of bmu - just enable strings
#        bmu_locs = som.output_bmu_locs
#        location_vects = som.output_location_vects
#        bmu_indices = som.output_bmu_indices

        #u-matrix data
        umatrix, bmu_loc = get_umatrix(input_data,weights, m, n)
        fig = plt.figure()
        plt.imshow(umatrix.reshape((m, n)),interpolation='gaussian',
                   cmap=plt.cm.gray)
        ax = plt.gca()
        ax.set_xticks(np.arange(0, n, 2))
        ax.set_yticks(np.arange(0, m, 2))
        ax.set_xticklabels(np.arange(1, n+1, 2))
        ax.set_yticklabels(np.arange(1, m+1, 2))
        plt.title('U_matrix')
        plt.show()
        fig.savefig(dir_im+'U_matrix.png', dpi = 150)



        # lets construct the colored image of weights
        w0 = weights[:, 0].reshape((m, n))
        w1 = weights[:, 1].reshape((m, n))
        w2 = weights[:, 2].reshape((m, n))
        w3 = weights[:, 3].reshape((m, n))

        # transform to color map
        im_weights_RGB = weights4_to_RGB(weights, m, n)

        fig = plt.figure()
        plt.imshow(im_weights_RGB, interpolation='gaussian')
        plt.show()


#       Sa is marked by "summer" color map
        fig = plt.figure()
        im_Sa = plt.imshow(w0,cmap = 'BrBG', interpolation='gaussian', 
                           vmin = w0.min(), vmax = w0.max())
        plt.colorbar(im_Sa)
        ax = plt.gca()
        ax.set_xticks(np.arange(0, n, 2))
        ax.set_yticks(np.arange(0, m, 2))
        ax.set_xticklabels(np.arange(1, n+1, 2))
        ax.set_yticklabels(np.arange(1, m+1, 2))
        plt.title('Sa weight matrix')
        plt.xlabel('neuron net '+str(m)+' x '+str(n))
        plt.show()
        fig.savefig(dir_im+'Sa weight matrix.png', dpi = 150)


#       Sq is marked by "winter" color map
        fig = plt.figure()
        im_Sq = plt.imshow(w1,cmap = 'bwr', interpolation='gaussian', 
                           vmin = w1.min(), vmax = w1.max())
        plt.colorbar(im_Sq)
        ax = plt.gca()
        ax.set_xticks(np.arange(0, n, 2))
        ax.set_yticks(np.arange(0, m, 2))
        ax.set_xticklabels(np.arange(1, n+1, 2))
        ax.set_yticklabels(np.arange(1, m+1, 2))
        plt.title('Sq weight matrix')
        plt.xlabel('neuron net '+str(m)+' x '+str(n))
        plt.show()
        fig.savefig(dir_im+'Sq weight matrix.png', dpi = 150)

#       Ssk is marked by "cool" color map
        fig = plt.figure()
        im_Ssk = plt.imshow(w2,cmap = 'PuOr', interpolation='gaussian', 
                            vmin = w2.min(), vmax = w2.max())
        plt.colorbar(im_Ssk)
        ax = plt.gca()
        ax.set_xticks(np.arange(0, n, 2))
        ax.set_yticks(np.arange(0, m, 2))
        ax.set_xticklabels(np.arange(1, n+1, 2))
        ax.set_yticklabels(np.arange(1, m+1, 2))
        plt.title('Ssk weight matrix')
        plt.xlabel('neuron net '+str(m)+' x '+str(n))
        plt.show()
        fig.savefig(dir_im+'Ssk weight matrix.png', dpi = 150)

#       Sku is marked by "RdBu" color map
        fig = plt.figure()
        im_Sku = plt.imshow(w3,cmap = 'RdBu', interpolation='gaussian', 
                            vmin = w3.min(), vmax = w3.max())
        plt.colorbar(im_Sku)
        ax = plt.gca()
        ax.set_xticks(np.arange(0, n, 2))
        ax.set_yticks(np.arange(0, m, 2))
        ax.set_xticklabels(np.arange(1, n+1, 2))
        ax.set_yticklabels(np.arange(1, m+1, 2))
        plt.title('Sku weight matrix')
        plt.xlabel('neuron net '+str(m)+' x '+str(n))
        plt.show()
        fig.savefig(dir_im+'Sku weight matrix.png', dpi = 150)


        
#       lets try to visualise location of sub surfaces)))
        output_location = np.zeros((m*subsurf_pxl, n*subsurf_pxl))  #shape have to be corrected   

#       lets make oneround correction
        corr_bmu = correction_bmu_location(bmu_loc)
        

#       calc the grouped location
        for i in range(len(corr_bmu)):
            indX, indY = corr_bmu[i]
            indX1 = indX*subsurf_pxl
            indX2 = indX1 + subsurf_pxl
            indY1 = indY*subsurf_pxl
            indY2 = indY1 + subsurf_pxl
            output_location[indX1:indX2, indY1:indY2] = sub_surf[i]

        fig = plt.figure()
        im_loc = plt.imshow(output_location, cmap=plt.cm.gray)
        ax = plt.gca()
        ax.set_xticks(np.arange(0, n*subsurf_pxl, subsurf_pxl*2))
        ax.set_yticks(np.arange(0, m*subsurf_pxl, subsurf_pxl*2))
        ax.set_xticklabels(np.arange(1, n+1, 2))
        ax.set_yticklabels(np.arange(1, m+1, 2))
        plt.title('U_Matrix for subimages')
        plt.show()
        fig.savefig(dir_im+'U_Matrix for subimages.png', dpi = 150)

        #   trying to overlap the surface and Sa
        extend_Sa_image = np.zeros((m*subsurf_pxl, n*subsurf_pxl))  #shape have to be corrected   
        tmp_arr = []
        for i in range (n):
            for j in range (m):
                tmp_arr = np.full((subsurf_pxl, subsurf_pxl), w0[j, i])
                indX1 = j*subsurf_pxl
                indX2 = indX1 + subsurf_pxl
                indY1 = i*subsurf_pxl
                indY2 = indY1 + subsurf_pxl
                extend_Sa_image[indX1:indX2, indY1:indY2] = tmp_arr 
        # overlapping colored images
        fig = plt.figure()
        im_1 = plt.imshow(output_location, cmap=plt.cm.gray)
        im_2 = plt.imshow(extend_Sa_image, cmap = 'BrBG', alpha = .3, 
                          interpolation='bilinear')
        ax = plt.gca()
        ax.set_xticks(np.arange(0, n*subsurf_pxl, subsurf_pxl*2))
        ax.set_yticks(np.arange(0, m*subsurf_pxl, subsurf_pxl*2))
        ax.set_xticklabels(np.arange(1, n+1, 2))
        ax.set_yticklabels(np.arange(1, m+1, 2))
        plt.title('U_Matrix for Sa of subimages')
        plt.colorbar(im_2)
        plt.show()
        fig.savefig(dir_im+'U_Matrix for Sa of subimages.png', dpi = 150)
        
        #   trying to overlap the surface and Sq
        extend_Sq_image = np.zeros((m*subsurf_pxl, n*subsurf_pxl))  #shape have to be corrected   
#        tmp_arr = []
        for i in range (n):
            for j in range (m):
                tmp_arr = np.full((subsurf_pxl, subsurf_pxl), w1[j, i])
                indX1 = j*subsurf_pxl
                indX2 = indX1 + subsurf_pxl
                indY1 = i*subsurf_pxl
                indY2 = indY1 + subsurf_pxl
                extend_Sq_image[indX1:indX2, indY1:indY2] = tmp_arr 
        # overlapping colored images
        fig = plt.figure()
        im_3 = plt.imshow(output_location, cmap=plt.cm.gray)
        im_4 = plt.imshow(extend_Sq_image, cmap = 'bwr', alpha = .3, 
                          interpolation='bilinear')
        ax = plt.gca()
        ax.set_xticks(np.arange(0, n*subsurf_pxl, subsurf_pxl*2))
        ax.set_yticks(np.arange(0, m*subsurf_pxl, subsurf_pxl*2))
        ax.set_xticklabels(np.arange(1, n+1, 2))
        ax.set_yticklabels(np.arange(1, m+1, 2))
        plt.title('U_Matrix for Sq of subimages')
        plt.colorbar(im_4)
        plt.show()
        fig.savefig(dir_im+'U_Matrix for Sq of subimages.png', dpi = 150)
        
        #   trying to overlap the surface and Ssk
        extend_Ssk_image = np.zeros((m*subsurf_pxl, n*subsurf_pxl))  
#        tmp_arr = []
        for i in range (n):
            for j in range (m):
                tmp_arr = np.full((subsurf_pxl, subsurf_pxl), w2[j, i])
                indX1 = j*subsurf_pxl
                indX2 = indX1 + subsurf_pxl
                indY1 = i*subsurf_pxl
                indY2 = indY1 + subsurf_pxl
                extend_Ssk_image[indX1:indX2, indY1:indY2] = tmp_arr 
        # overlapping images
        fig = plt.figure()
        im_5 = plt.imshow(output_location, cmap=plt.cm.gray)
        im_6 = plt.imshow(extend_Ssk_image, cmap = 'PuOr', alpha = .3, 
                          interpolation='bilinear')
        ax = plt.gca()
        ax.set_xticks(np.arange(0, n*subsurf_pxl, subsurf_pxl*2))
        ax.set_yticks(np.arange(0, m*subsurf_pxl, subsurf_pxl*2))
        ax.set_xticklabels(np.arange(1, n+1, 2))
        ax.set_yticklabels(np.arange(1, m+1, 2))
        plt.title('U_Matrix for Ssk of subimages')
        plt.colorbar(im_6)
        plt.show()
        fig.savefig(dir_im+'U_Matrix for Ssk of subimages.png', dpi = 150)
        
        #   trying to overlap the surface and Sku
        extend_Sku_image = np.zeros((m*subsurf_pxl, n*subsurf_pxl))
#        tmp_arr = []
        for i in range (n):
            for j in range (m):
                tmp_arr = np.full((subsurf_pxl, subsurf_pxl), w3[j, i])
                indX1 = j*subsurf_pxl
                indX2 = indX1 + subsurf_pxl
                indY1 = i*subsurf_pxl
                indY2 = indY1 + subsurf_pxl
                extend_Sku_image[indX1:indX2, indY1:indY2] = tmp_arr 
        # overlapping images
        fig = plt.figure()
        im_7 = plt.imshow(output_location, cmap=plt.cm.gray)
        im_8 = plt.imshow(extend_Sku_image, cmap = 'RdBu', alpha = .3, 
                          interpolation='bilinear')
        ax = plt.gca()
        ax.set_xticks(np.arange(0, n*subsurf_pxl, subsurf_pxl*2))
        ax.set_yticks(np.arange(0, m*subsurf_pxl, subsurf_pxl*2))
        ax.set_xticklabels(np.arange(1, n+1, 2))
        ax.set_yticklabels(np.arange(1, m+1, 2))
        plt.title('U_Matrix for Sku of subimages')
        plt.colorbar(im_8)
        plt.show()
        fig.savefig(dir_im+'U_Matrix for Sku of subimages.png', dpi = 150)
        
        print('Done!')
        
        # trying to make the trace back to the place of origin...
        a_Sa = np.append(w0.reshape(umatrix.shape), 
                         np.full(corr_bmu.shape[0]-w0.reshape(umatrix.shape).shape[0],0))
        surf_add_Sa = np.full_like(s_data, 0)
        for ind_i in range(len(list(a_Sa))):
            tmp_color = w0[corr_bmu[ind_i,0],corr_bmu[ind_i,1]]
            tmp_m = np.full((subsurf_pxl, subsurf_pxl), tmp_color)
            indX1, indY1 = sub_surf_ind[ind_i]
            indX2 = indX1 + subsurf_pxl
            indY2 = indY1 + subsurf_pxl
            
            surf_add_Sa[indX1:indX2, indY1:indY2] = tmp_m
            
        # overlapping real surface with Sa
        fig = plt.figure()
        fig.set_figwidth(fig.get_figwidth()*2)
        fig.set_figheight(fig.get_figheight()*2)  
        im_1Sa = plt.imshow(s_data, cmap=plt.cm.gray, 
                            extent=[s_params[1] // 1000, s_params[0] // 1000, s_params[3] // 1000, s_params[2] // 1000])
        im_2Sa = plt.imshow(surf_add_Sa, cmap = 'BrBG', alpha = .3, 
                            interpolation='bilinear', 
                            extent=[s_params[1] // 1000, s_params[0] // 1000, s_params[3] // 1000, s_params[2] // 1000])

        plt.xlabel('Friction distance ($\mu $m)')
        plt.ylabel('Friction width ($\mu $m)')
        plt.title('Rough surface with a colored mask of Sa')
        plt.show()
        fig.savefig(dir_im+'Rough surface with a colored mask of Sa.png', dpi = 150)

        # overlapping real surface with Sq
        a_Sq = np.append(w1.reshape(umatrix.shape), 
                         np.full(corr_bmu.shape[0]-w1.reshape(umatrix.shape).shape[0],0))
        surf_add_Sq = np.full_like(s_data, 0)
        for ind_i in range(len(list(a_Sq))):
            tmp_color = w1[corr_bmu[ind_i,0],corr_bmu[ind_i,1]]
            tmp_m = np.full((subsurf_pxl, subsurf_pxl), tmp_color)
            indX1, indY1 = sub_surf_ind[ind_i]
            indX2 = indX1 + subsurf_pxl
            indY2 = indY1 + subsurf_pxl
            
            surf_add_Sq[indX1:indX2, indY1:indY2] = tmp_m
        
        fig = plt.figure()
        fig.set_figwidth(fig.get_figwidth()*2)
        fig.set_figheight(fig.get_figheight()*2)  
        im_3Sq = plt.imshow(s_data, cmap=plt.cm.gray, 
                            extent=[s_params[1] // 1000, s_params[0] // 1000, s_params[3] // 1000, s_params[2] // 1000])
        im_4Sq = plt.imshow(surf_add_Sq, cmap = 'bwr', alpha = .3, 
                            interpolation='bilinear', 
                            extent=[s_params[1] // 1000, s_params[0] // 1000, s_params[3] // 1000, s_params[2] // 1000])

        plt.xlabel('Friction distance ($\mu $m)')
        plt.ylabel('Friction width ($\mu $m)')
        plt.title('Rough surface with a colored mask of Sq')
        plt.show()
        fig.savefig(dir_im+'Rough surface with a colored mask of Sq.png', dpi = 150)

        # overlapping real surface with Ssk
        a_Ssk = np.append(w2.reshape(umatrix.shape), 
                         np.full(corr_bmu.shape[0]-w2.reshape(umatrix.shape).shape[0],0))
        surf_add_Ssk = np.full_like(s_data, 0)
        for ind_i in range(len(list(a_Ssk))):
            tmp_color = w2[corr_bmu[ind_i,0],corr_bmu[ind_i,1]]
            tmp_m = np.full((subsurf_pxl, subsurf_pxl), tmp_color)
            indX1, indY1 = sub_surf_ind[ind_i]
            indX2 = indX1 + subsurf_pxl
            indY2 = indY1 + subsurf_pxl
            
            surf_add_Ssk[indX1:indX2, indY1:indY2] = tmp_m
        
        fig = plt.figure()
        fig.set_figwidth(fig.get_figwidth()*2)
        fig.set_figheight(fig.get_figheight()*2)  
        im_5Ssk = plt.imshow(s_data, cmap=plt.cm.gray, 
                            extent=[s_params[1] // 1000, s_params[0] // 1000, s_params[3] // 1000, s_params[2] // 1000])
        im_6Ssk = plt.imshow(surf_add_Ssk, cmap = 'PuOr', alpha = .3, 
                            interpolation='bilinear', 
                            extent=[s_params[1] // 1000, s_params[0] // 1000, s_params[3] // 1000, s_params[2] // 1000])

        plt.xlabel('Friction distance ($\mu $m)')
        plt.ylabel('Friction width ($\mu $m)')
        plt.title('Rough surface with a colored mask of Ssk')
        plt.show()
        fig.savefig(dir_im+'Rough surface with a colored mask of Ssk.png', dpi = 150)
            
        # overlapping real surface with Sku
        a_Sku = np.append(w3.reshape(umatrix.shape), 
                         np.full(corr_bmu.shape[0]-w3.reshape(umatrix.shape).shape[0],0))
        surf_add_Sku = np.full_like(s_data, 0)
        for ind_i in range(len(list(a_Sku))):
            tmp_color = w3[corr_bmu[ind_i,0],corr_bmu[ind_i,1]]
            tmp_m = np.full((subsurf_pxl, subsurf_pxl), tmp_color)
            indX1, indY1 = sub_surf_ind[ind_i]
            indX2 = indX1 + subsurf_pxl
            indY2 = indY1 + subsurf_pxl
            
            surf_add_Sku[indX1:indX2, indY1:indY2] = tmp_m
        
        fig = plt.figure()
        fig.set_figwidth(fig.get_figwidth()*2)
        fig.set_figheight(fig.get_figheight()*2)  
        im_7Sku = plt.imshow(s_data, cmap=plt.cm.gray, 
                            extent=[s_params[1] // 1000, s_params[0] // 1000, s_params[3] // 1000, s_params[2] // 1000])
        im_8Sku = plt.imshow(surf_add_Sku, cmap = 'RdBu', alpha = .3, 
                            interpolation='bilinear', 
                            extent=[s_params[1] // 1000, s_params[0] // 1000, s_params[3] // 1000, s_params[2] // 1000])

        plt.xlabel('Friction distance ($\mu $m)')
        plt.ylabel('Friction width ($\mu $m)')
        plt.title('Rough surface with a colored mask of Sku')
        plt.show()
        fig.savefig(dir_im+'Rough surface with a colored mask of Sku.png', dpi = 150)
    
    