import { Box, Spinner } from '@cloudscape-design/components';
import React, { useEffect, useState } from 'react';
import { StepContentProps } from './AIPhotoWizard';

const API_ENDPOINT = window.API_ENDPOINT;
// const API_ENDPOINT = 'https://c5jduogr78.execute-api.us-east-1.amazonaws.com/prod';
const API_SUBPATH = '/human-segmentation';

const CompositeStep = ({ request, setRequest }: StepContentProps) => {
  const [isLoading, setIsLoading] = useState(true);
  // const [composite, setComposite] = useState('');

  useEffect(() => {
    const composite = async () => {
      try {
        // Call AI solution kit API to get human segmentation
        const res = await fetch(API_ENDPOINT + API_SUBPATH, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            img: request.portrait?.substr(request.portrait?.indexOf(',')),  // Remove prefix like "data:image/jpeg;base64,"
            type: 'foreground'
          })
        });
        const imgData = await res.json();

        // Merge images
        const canvas = document.createElement('canvas');
        canvas.height = 1120;
        canvas.width = 630;

        const loadImage = (dataURL: string): Promise<HTMLImageElement> => {
          return new Promise((resolve) => {
            const img = new Image();
            img.src = dataURL;
            img.onload = () => resolve(img);
          });
        }

        if (request.background) {
          const bg = await loadImage(request.background);
          canvas.getContext('2d')!.drawImage(bg, 0, 0, 630, 1120);
        }

        const portrait = await loadImage('data:image/png;base64,' + imgData.result);
        canvas.getContext('2d')!.drawImage(portrait, 30, 100, 570, 1020);

        if (request.logo) {
          const logo = await loadImage(request.logo);
          canvas.getContext('2d')!.drawImage(logo, 20, 20);
        }

        if (request.slogan) {
          const slogan = await loadImage(request.slogan);
          canvas.getContext('2d')!.drawImage(slogan, (630 - slogan.width) / 2, 900 - slogan.height);
        }

        setRequest({
          ...request,
          composite: canvas.toDataURL()
        });
        setIsLoading(false);
      } catch (e) {
        console.error(e);
      }
    }

    composite();
  }, []);

  return (
    <>
      {isLoading ?
        <Box textAlign="center">
          <Spinner size="big" />
          <Box variant="h2" margin='xl'>正在合成照片，请稍后...</Box>
        </Box> :
        <Box textAlign="center">
          <img src={request.composite} alt='composite' />
        </Box>
      }
    </>
  );
};

export default CompositeStep;
