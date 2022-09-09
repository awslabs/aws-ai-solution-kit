import { Alert, Box, Container, Grid, Wizard } from '@cloudscape-design/components';
import React, { Dispatch, SetStateAction, useEffect, useState } from 'react';
import BackgroundStep from './BackgroundStep';
import CompositeStep from './CompositeStep';
import TakePhotoStep from './TakePhotoStep';

interface PhotoRequest {
  readonly background?: string;
  readonly logo?: string;
  readonly slogan?: string;
  readonly portrait?: string;
  readonly composite?: string;
}

export interface StepContentProps {
  readonly setIsLoadingNextStep: Dispatch<SetStateAction<boolean>>;
  readonly request: PhotoRequest;
  readonly setRequest: Dispatch<SetStateAction<PhotoRequest>>;
}

interface PhotoWizardStep {
  readonly title: string;
  readonly StepContent: React.FC<StepContentProps>
}

const i18nStrings = {
  stepNumberLabel: (stepNumber: number) => `第${stepNumber}步`,
  collapsedStepsLabel: (stepNumber: number, stepsCount: number) => `第${stepNumber}/${stepsCount}步`,
  cancelButton: '取消',
  previousButton: '上一步',
  nextButton: '下一步',
  submitButton: '保存图片',
  optional: '可选'
};

const steps: PhotoWizardStep[] = [
  {
    title: '选择图片',
    StepContent: BackgroundStep
  },
  {
    title: '拍摄照片',
    StepContent: TakePhotoStep
  },
  {
    title: '合成照片',
    StepContent: CompositeStep
  }
];

const AIPhotoWizard = () => {
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [isLoadingNextStep, setIsLoadingNextStep] = useState(false);
  const [request, setRequest] = useState<PhotoRequest>({});
  const [alertContent, setAlertContent] = useState('');

  const wizardSteps = steps.map(({ title, StepContent }) => ({
    title,
    content: (
      <>
        <Container>
          <StepContent setIsLoadingNextStep={setIsLoadingNextStep} request={request} setRequest={setRequest} />
        </Container>
        <Grid gridDefinition={[{ colspan: 6, offset: 3 }]}>
          <Box margin={{ top: 'xxl' }}>
            <Alert visible={!!alertContent} type="error">
              {alertContent}
            </Alert>
          </Box>
        </Grid>
      </>
    )
  }));

  const onNavigate = ({ detail }: any) => {
    const next = detail.requestedStepIndex;

    // Validation check for background confirmation
    if (next === 1 && !request.background) {
      setAlertContent('请选择背景图片！');
      return;
    }

    if (next === 2 && !request.portrait) {
      setAlertContent('请拍摄照片！');
      return;
    }

    setAlertContent('');
    setActiveStepIndex(next);
  }

  return (
    <Wizard
      steps={wizardSteps}
      activeStepIndex={activeStepIndex}
      onNavigate={onNavigate}
      onCancel={() => {
        window.location.reload();
      }}
      onSubmit={() => {
        const link = document.createElement('a');
        link.download = 'image.png';
        link.href = request.composite || '';
        link.click();
      }}
      isLoadingNextStep={isLoadingNextStep}
      i18nStrings={i18nStrings}
    />
  );
}

export default AIPhotoWizard;