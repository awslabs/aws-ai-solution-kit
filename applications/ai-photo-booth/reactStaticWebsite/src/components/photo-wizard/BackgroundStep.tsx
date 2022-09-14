import { Box, Button, Cards, Header, Toggle } from '@cloudscape-design/components';
import React, { useEffect, useState } from 'react';
import { StepContentProps } from './AIPhotoWizard';

export interface ImageItem {
  readonly name: string,
  readonly src: string
}

const MAX_IMAGE_COUNT = 4;

/**
 * Get image items for Card component
 *
 * @param type ['bg', 'logo', 'slogan']
 * @param typeName ['背景图片', 'Logo', '标语']
 */
const getImageItems = async (type: string, typeName: string): Promise<ImageItem[]> => {
  const items = [];

  const imageExists = (name: string, ext: string): Promise<boolean> => {
    return new Promise((resolve) => {
      const img = new Image();
      img.src = name + '.' + ext;
      img.onerror = () => resolve(false); // Ignore image not existing error
      img.onload = () => resolve(img.height > 0)
    });
  }

  for (let i = 1; i <= MAX_IMAGE_COUNT; i++) {
    const fileName = `/images/${type}_${i}`;
    let filePath: string = '';

    // Search for .jpg, .jpeg and .pgn images
    if (await imageExists(fileName, 'jpg')) {
      filePath = fileName + '.jpg';
    } else if (await imageExists(fileName, 'jpeg')) {
      filePath = fileName + '.jpeg';
    } else if (await imageExists(fileName, 'png')) {
      filePath = fileName + '.png';
    }

    if (!!filePath) {
      items.push({
        name: `${typeName}${i}`,
        src: filePath
      });
    }
  }

  return items;
};

const toDataURL = (src: string): Promise<string> => {
  return new Promise(resolve => {
    const image = new Image();
    image.crossOrigin = 'Anonymous';
    image.src = src;
    image.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.height = image.naturalHeight;
      canvas.width = image.naturalWidth;
      canvas.getContext('2d')!.drawImage(image, 0, 0);
      resolve(canvas.toDataURL());
    };
  });
};

const BackgroundStep = ({ request, setRequest }: StepContentProps) => {
  const [bgItems, setBgItems] = useState<ImageItem[]>([]);
  const [logoItems, setLogoItems] = useState<ImageItem[]>([]);
  const [sloganItems, setSloganItems] = useState<ImageItem[]>([]);
  const [selectedBackground, setSelectedBackground] = useState<ImageItem>();
  const [selectedLogo, setSelectedLogo] = useState<ImageItem>();
  const [selectedSlogan, setSelectedSlogan] = useState<ImageItem>();
  const [checkLogoDarkBg, setCheckLogoDarkBg] = useState(false);
  const [checkSloganDarkBg, setCheckSloganDarkBg] = useState(false);

  useEffect(() => {
    const setImageItems = async () => {
      setBgItems(await getImageItems('bg', '背景图片'));
      setLogoItems(await getImageItems('logo', 'Logo'));
      setSloganItems(await getImageItems('slogan', '标语'));
    }

    setImageItems();
  }, []);

  useEffect(() => {
    const setRequestBackground = async () => {
      let base64 = undefined;
      if (selectedBackground?.src) {
        base64 = await toDataURL(selectedBackground?.src);
      }

      setRequest({
        ...request,
        background: base64
      });
    }

    setRequestBackground();
  }, [selectedBackground]);

  useEffect(() => {
    const setRequestLogo = async () => {
      let base64 = undefined;
      if (selectedLogo?.src) {
        base64 = await toDataURL(selectedLogo?.src);
      }

      setRequest({
        ...request,
        logo: base64
      });
    }

    setRequestLogo();
  }, [selectedLogo]);

  useEffect(() => {
    const setRequestSlogan = async () => {
      let base64 = undefined;
      if (selectedSlogan?.src) {
        base64 = await toDataURL(selectedSlogan?.src);
      }

      setRequest({
        ...request,
        slogan: base64
      });
    }

    setRequestSlogan();
  }, [selectedSlogan]);

  return (
    <>
      <Box>
        <Box variant="h2">说明</Box>
        <Box>
          <ul>
            <li>上传背景图片、Logo、Slogan至相应S3 bucket的<strong>images</strong>文件夹下</li>
            <li>每种类型最多可上传{MAX_IMAGE_COUNT}张图片，支持图片类型：.jpg, .jpeg, .png</li>
            <li>
              图片命名规则：<strong>&lt;图片类型&gt;_&lt;序号&gt;.&lt;扩展名&gt;</strong>，示例: <i>logo_2.png</i>
              <ul>
                <li>图片类型：bg | logo | slogan</li>
                <li>序号：1 - {MAX_IMAGE_COUNT}</li>
                <li>扩展名：jpg | jpeg | png</li>
              </ul>
            </li>
            <li>背景图片为必选，Logo和标语Slogan为可选</li>
            <li>预览Logo和标语Slogan可切换背景颜色</li>
          </ul>
        </Box>
      </Box>
      <hr />
      <Box margin={{ vertical: 'xl' }}>
        <Header variant="h2">选择背景图片</Header>
      </Box>
      <Cards
        onSelectionChange={({ detail }) => setSelectedBackground(detail.selectedItems[0] as ImageItem)}
        selectedItems={[selectedBackground]}
        cardDefinition={{
          header: (e: ImageItem) => e.name,
          sections: [
            {
              id: 'image',
              content: (e: ImageItem) => (
                <Box padding={'xl'}>
                  <img src={e.src} width={300} height={568} alt={e.name} />
                </Box>
              )
            }
          ]
        }}
        items={bgItems}
        selectionType="single"
        cardsPerRow={[
          { cards: 1 },
          { minWidth: 800, cards: 2 }
        ]}
      />
      <hr />
      <Box margin={{ vertical: 'xl' }}>
        <Header variant="h2" actions={
          <>
            <Box padding={{ vertical: 'xs' }} display={'inline-block'}>
              <Toggle checked={checkLogoDarkBg} onChange={({ detail }) => setCheckLogoDarkBg(detail.checked)} />
            </Box>
            <Box variant="span" padding={'xs'}>切换深色背景</Box>
            <Box margin={{ left: 'l' }}>
              <Button onClick={() => setSelectedLogo(undefined)}>取消选择</Button>
            </Box>
          </>
        }>
          选择Logo
        </Header>
      </Box>
      <Cards
        onSelectionChange={({ detail }) => setSelectedLogo(detail.selectedItems[0] as ImageItem)}
        selectedItems={[selectedLogo]}
        cardDefinition={{
          header: (e: ImageItem) => e.name,
          sections: [
            {
              id: 'image',
              content: (e: ImageItem) => (
                <div style={{ background: checkLogoDarkBg ? 'black' : 'white' }}>
                  <Box padding={'xl'}>
                    <img src={e.src} width={300} height={120} alt={e.name} />
                  </Box>
                </div>
              )
            }
          ]
        }}
        items={logoItems}
        selectionType="single"
        cardsPerRow={[
          { cards: 1 },
          { minWidth: 800, cards: 2 }
        ]}
      />
      <hr />
      <Box margin={{ vertical: 'xl' }}>
        <Header variant="h2" actions={
          <>
            <Box padding={{ vertical: 'xs' }} display={'inline-block'}>
              <Toggle checked={checkSloganDarkBg} onChange={({ detail }) => setCheckSloganDarkBg(detail.checked)} />
            </Box>
            <Box variant="span" padding={'xs'}>切换深色背景</Box>
            <Box margin={{ left: 'l' }}>
              <Button onClick={() => setSelectedSlogan(undefined)}>取消选择</Button>
            </Box>
          </>
        }>
          选择标语Slogan
        </Header>
      </Box>
      <Cards
        onSelectionChange={({ detail }) => setSelectedSlogan(detail.selectedItems[0] as ImageItem)}
        selectedItems={[selectedSlogan]}
        cardDefinition={{
          header: (e: ImageItem) => e.name,
          sections: [
            {
              id: 'image',
              content: (e: ImageItem) => (
                <div style={{ background: checkSloganDarkBg ? 'black' : 'white' }}>
                  <Box padding={'xl'}>
                    <img src={e.src} width={300} height={120} alt={e.name} />
                  </Box>
                </div>
              )
            }
          ]
        }}
        items={sloganItems}
        selectionType="single"
        cardsPerRow={[
          { cards: 1 },
          { minWidth: 800, cards: 2 }
        ]}
      />
    </>
  );
};

export default BackgroundStep;
