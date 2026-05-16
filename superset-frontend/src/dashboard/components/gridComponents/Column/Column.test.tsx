/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import React from 'react';
import { fireEvent, render } from 'spec/helpers/testing-library';

import { getMockStore } from 'spec/fixtures/mockStore';
import { dashboardLayout as mockLayout } from 'spec/fixtures/mockDashboardLayout';
import { initialState } from 'src/SqlLab/fixtures';
import ColumnComponent from './Column';

// Cast to accept partial mock props in tests
const Column = ColumnComponent as unknown as React.FC<Record<string, unknown>>;

jest.mock('src/dashboard/components/dnd/DragDroppable', () => ({
  Draggable: ({
    children,
  }: {
    children: (arg: Record<string, unknown>) => React.ReactNode;
  }) => <div data-test="mock-draggable">{children({})}</div>,
  Droppable: ({
    children,
    depth,
  }: {
    children: (arg: Record<string, unknown>) => React.ReactNode;
    depth: number;
  }) => (
    <div data-test="mock-droppable" data-depth={depth}>
      {children({})}
    </div>
  ),
}));
jest.mock(
  'src/dashboard/containers/DashboardComponent',
  () =>
    ({
      availableColumnCount,
      depth,
    }: {
      availableColumnCount: number;
      depth: number;
    }) => (
      <div data-test="mock-dashboard-component" data-depth={depth}>
        {availableColumnCount}
      </div>
    ),
);
jest.mock(
  'src/dashboard/components/menu/WithPopoverMenu',
  () =>
    ({
      children,
      menuItems,
      isFocused,
      editMode,
    }: {
      children: React.ReactNode;
      menuItems?: React.ReactNode[];
      isFocused?: boolean;
      editMode?: boolean;
    }) => (
      <div data-test="mock-with-popover-menu">
        {children}
        {editMode && isFocused && menuItems}
      </div>
    ),
);
jest.mock(
  'src/dashboard/components/menu/BackgroundStyleDropdown',
  () =>
    ({ id }: { id: string }) => (
      <div data-test="mock-background-style-dropdown" data-id={id} />
    ),
);
jest.mock(
  'src/dashboard/components/resizable/ResizableContainer',
  () =>
    ({
      children,
      adjustableWidth,
      adjustableHeight,
      widthStep,
      widthMultiple,
      minWidthMultiple,
      maxWidthMultiple,
    }: {
      children: React.ReactNode;
      adjustableWidth: boolean;
      adjustableHeight: boolean;
      widthStep: number;
      widthMultiple: number;
      minWidthMultiple: number;
      maxWidthMultiple: number;
    }) => (
      <div
        className="resizable-container"
        data-test="mock-resizable-container"
        data-adjustable-width={String(adjustableWidth)}
        data-adjustable-height={String(adjustableHeight)}
        data-width-step={String(widthStep)}
        data-width-multiple={String(widthMultiple)}
        data-min-width-multiple={String(minWidthMultiple)}
        data-max-width-multiple={String(maxWidthMultiple)}
      >
        {children}
      </div>
    ),
);
jest.mock(
  'src/dashboard/components/DeleteComponentButton',
  () =>
    ({ onDelete }: { onDelete: () => void }) => (
      <button
        type="button"
        data-test="mock-delete-component-button"
        onClick={onDelete}
      >
        Delete
      </button>
    ),
);

const columnWithoutChildren = {
  ...mockLayout.present.COLUMN_ID,
  children: [],
};
const props = {
  id: 'COLUMN_ID',
  parentId: 'ROW_ID',
  component: mockLayout.present.COLUMN_ID,
  parentComponent: mockLayout.present.ROW_ID,
  index: 0,
  depth: 2,
  editMode: false,
  availableColumnCount: 12,
  minColumnWidth: 2,
  columnWidth: 50,
  occupiedColumnCount: 6,
  onResizeStart() {},
  onResize() {},
  onResizeStop() {},
  handleComponentDrop() {},
  deleteComponent() {},
  updateComponents() {},
};

function setup(overrideProps: Record<string, unknown> = {}) {
  // We have to wrap provide DragDropContext for the underlying DragDroppable
  // otherwise we cannot assert on DragDroppable children
  const mockStore = getMockStore({
    ...initialState,
  });
  return render(<Column {...props} {...overrideProps} />, {
    store: mockStore,
    useDnd: true,
    useRouter: true,
  });
}

test('should render a Draggable', () => {
  const { getByTestId, queryByTestId } = setup({
    component: columnWithoutChildren,
  });
  expect(getByTestId('mock-draggable')).toBeInTheDocument();
  expect(queryByTestId('mock-droppable')).not.toBeInTheDocument();
});

test('should skip rendering HoverMenu and DeleteComponentButton when not in editMode', () => {
  const { container, queryByTestId } = setup({
    component: columnWithoutChildren,
  });
  expect(container.querySelector('.hover-menu')).not.toBeInTheDocument();
  expect(queryByTestId('mock-delete-component-button')).not.toBeInTheDocument();
});

test('should render a WithPopoverMenu', () => {
  // don't count child DragDroppables
  const { getByTestId } = setup({ component: columnWithoutChildren });
  expect(getByTestId('mock-with-popover-menu')).toBeInTheDocument();
});

test('should render a ResizableContainer', () => {
  // don't count child DragDroppables
  const { container } = setup({ component: columnWithoutChildren });
  expect(container.querySelector('.resizable-container')).toBeInTheDocument();
});

test('should render a HoverMenu in editMode', () => {
  // we cannot set props on the Row because of the WithDragDropContext wrapper
  const { container, getAllByTestId, getByTestId } = setup({
    component: columnWithoutChildren,
    editMode: true,
  });
  expect(container.querySelector('.hover-menu')).toBeInTheDocument();

  // Droppable area enabled in editMode
  expect(getAllByTestId('mock-droppable').length).toBe(1);

  // pass the same depth of its droppable area
  expect(getByTestId('mock-droppable')).toHaveAttribute(
    'data-depth',
    `${props.depth}`,
  );
});

test('should render a DeleteComponentButton in editMode', () => {
  // we cannot set props on the Row because of the WithDragDropContext wrapper
  const { getByTestId } = setup({
    component: columnWithoutChildren,
    editMode: true,
  });
  expect(getByTestId('mock-delete-component-button')).toBeInTheDocument();
});

test('should render a BackgroundStyleDropdown when focused', () => {
  const { queryByTestId, getAllByRole } = setup({
    component: columnWithoutChildren,
    editMode: true,
  });
  expect(
    queryByTestId('mock-background-style-dropdown'),
  ).not.toBeInTheDocument();

  // click the settings IconButton to focus the column
  const buttons = getAllByRole('button');
  const settingsButton = buttons.find(
    btn => btn.getAttribute('data-test') !== 'mock-delete-component-button',
  )!;
  fireEvent.click(settingsButton);

  expect(queryByTestId('mock-background-style-dropdown')).toBeInTheDocument();
});

test('should call deleteComponent when deleted', () => {
  const deleteComponent = jest.fn();
  const { getByTestId } = setup({ editMode: true, deleteComponent });
  fireEvent.click(getByTestId('mock-delete-component-button'));
  expect(deleteComponent).toHaveBeenCalledTimes(1);
});

test('should pass its own width as availableColumnCount to children', () => {
  const { getByTestId } = setup();
  expect(getByTestId('mock-dashboard-component')).toHaveTextContent(
    String(props.component.meta.width),
  );
});

test('should pass appropriate dimensions to ResizableContainer', () => {
  const { getByTestId } = setup({ component: columnWithoutChildren });
  const columnWidth = columnWithoutChildren.meta.width;
  const resizable = getByTestId('mock-resizable-container');

  expect(resizable).toHaveAttribute('data-adjustable-width', 'true');
  expect(resizable).toHaveAttribute('data-adjustable-height', 'false');
  expect(resizable).toHaveAttribute(
    'data-width-step',
    String(props.columnWidth),
  );
  expect(resizable).toHaveAttribute('data-width-multiple', String(columnWidth));
  expect(resizable).toHaveAttribute(
    'data-min-width-multiple',
    String(props.minColumnWidth),
  );
  expect(resizable).toHaveAttribute(
    'data-max-width-multiple',
    String(props.availableColumnCount + columnWidth),
  );
});

test('should render between-items Droppables for each child in editMode', () => {
  const { getAllByTestId } = setup({ editMode: true });
  // 1 top-edge droptarget + 1 after-child droptarget = 2 total
  const droppables = getAllByTestId('mock-droppable');
  expect(droppables).toHaveLength(2);
  droppables.forEach(droppable => {
    expect(droppable).toHaveAttribute('data-depth', `${props.depth}`);
  });
});

test('should increment the depth of its children', () => {
  const { getByTestId } = setup();
  expect(getByTestId('mock-dashboard-component')).toHaveAttribute(
    'data-depth',
    `${props.depth + 1}`,
  );
});
