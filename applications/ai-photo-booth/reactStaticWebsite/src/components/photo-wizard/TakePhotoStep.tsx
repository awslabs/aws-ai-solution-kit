import { Box, Button } from '@cloudscape-design/components';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import Webcam from 'react-webcam';
import { StepContentProps } from './AIPhotoWizard';

const videoConstraints = {
  width: 630,
  height: 1120,
  facingMode: 'user'
};

const COUNT_DOWN_TIME = 5;

const TakePhotoStep = ({ request, setRequest }: StepContentProps) => {
  // const [image, setImage] = useState<string | null>('');
  const [takePhotoBtnText, setTakePhotoBtnText] = useState('拍照');
  const [countDownTime, setCountDownTime] = useState(COUNT_DOWN_TIME);
  const [startCountDown, setStartCountDown] = useState(false);
  const webcamRef = useRef<Webcam>(null);

  const capture = useCallback(() => {
    if (webcamRef && webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      setRequest({
        ...request,
        portrait: imageSrc || undefined
      })
    }
  }, [webcamRef]);

  useEffect(() => {
    if (startCountDown) {
      setTakePhotoBtnText(`倒计时 ${countDownTime} 秒`);
      const timeout = setTimeout(() => {
        setCountDownTime(countDownTime - 1);

        // Take photo when count down to 0
        if (countDownTime === 0) {
          setStartCountDown(false);

          capture();
        }
      }, 1000);

      return () => {
        clearTimeout(timeout);
      }
    }
  }, [startCountDown, countDownTime]);

  return (
    <div>
      {!!request.portrait ?
        <Box textAlign="center">
          <img src={request.portrait} alt='portrait' />
          <Button onClick={() => {
            setRequest({ ...request, portrait: undefined });
            setCountDownTime(COUNT_DOWN_TIME);
            setTakePhotoBtnText('拍照');
          }}>重新拍照</Button>
        </Box> :
        <Box textAlign="center">
          <Webcam
            audio={false}
            width={1120}
            height={630}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
          />
          <Button onClick={() => setStartCountDown(true)}>{takePhotoBtnText}</Button>
        </Box>
      }
    </div>
  );
};

export default TakePhotoStep;
