/*
The contents of this file are subject to the Mozilla Public License Version 1.1
(the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS" basis, WITHOUT
WARRANTY OF ANY KIND, either express or implied. See the License for the specific
language governing rights and limitations under the License.

The Original Code is "IntegerPanel.java". Description:
"Input Panel for entering Integers

  @author Shu Wu"

The Initial Developer of the Original Code is Bryan Tripp & Centre for Theoretical Neuroscience, University of Waterloo. Copyright (C) 2006-2008. All Rights Reserved.

Alternatively, the contents of this file may be used under the terms of the GNU
Public License license (the GPL License), in which case the provisions of GPL
License are applicable  instead of those above. If you wish to allow use of your
version of this file only under the terms of the GPL License and not to allow
others to use your version of this file under the MPL, indicate your decision
by deleting the provisions above and replace  them with the notice and other
provisions required by the GPL License.  If you do not delete the provisions above,
a recipient may use your version of this file under either the MPL or the GPL License.
 */

package ca.nengo.ui.configurable.panels;

import javax.swing.JTextField;

import ca.nengo.ui.configurable.PropertyInputPanel;
import ca.nengo.ui.configurable.descriptors.PInt;

/**
 * Input Panel for entering Integers
 * 
 * @author Shu Wu
 */
public class IntegerPanel extends PropertyInputPanel {

    public JTextField tf;

    /**
     * @param property TODO
     */
    public IntegerPanel(PInt property) {
        super(property);
        initPanel();
    }

    @Override
    public PInt getDescriptor() {
        return (PInt) super.getDescriptor();
    }

    @Override
    public Integer getValue() {

        Integer integerValue = new Integer(tf.getText());
        return integerValue.intValue();

    }

    public void initPanel() {
        tf = new JTextField(10);

        add(tf);

    }



    @Override
    public boolean isValueSet() {
        String textValue = tf.getText();

        if (textValue == null || textValue.compareTo("") == 0) {
            return false;
        }

        try {
            Integer value = getValue();

            if (getDescriptor().isCheckRange()) {
                if (value > getDescriptor().getMax()
                        || value < getDescriptor().getMin()) {
                    return false;
                }
            }

        } catch (NumberFormatException e) {
        	setStatusMsg("Invalid number format");
            return false;
        }

        setStatusMsg("");
        return true;
    }

    @Override
    public void setValue(Object value) {
        tf.setText(value.toString());
    }

    @Override
    public void setEnabled(boolean enabled) {
        super.setEnabled(enabled);
        tf.setEnabled(enabled);
    }

}