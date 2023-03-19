import React from 'react';

const style = {
  overflow: 'auto',
};

/**
 * Display an svg image. This is needed to be able to handle overflow in
 * larger images.
 *
 * ```mdx
 * import svgUrl from "!url-loader!./path/to/image.svg";
 * import { SvgImage } from "@site/src/components/SvgImage";
 * <SvgImage href={svgUrl} />
 * ```
 */
export function SvgImage(props) {
  const { href } = props;
  return (
    <div style={style}>
      <object data={href} />
    </div>
  );
}
