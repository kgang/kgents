/**
 * HorizontalRuleToken — Visual section divider.
 *
 * Renders ---, ***, or ___ as a styled horizontal rule.
 *
 * "Visual section divider."
 */

import { memo } from 'react';

import './tokens.css';

interface HorizontalRuleTokenProps {
  className?: string;
}

export const HorizontalRuleToken = memo(function HorizontalRuleToken({
  className,
}: HorizontalRuleTokenProps) {
  return <hr className={`horizontal-rule-token ${className ?? ''}`} />;
});
